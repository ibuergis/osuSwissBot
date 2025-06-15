import ossapi.enums
import requests

import re
import io

from src.helper.osuHelper import handleModToString, modStringToList

import ossapi
from ossapi import User, Score, Beatmap
from ossapi.models import DifficultyAttributes

from PIL import Image, ImageEnhance, ImageFont, ImageDraw, ImageFilter

rankedAlias = {
    ossapi.enums.RankStatus.RANKED:    'data/rankedStatus/ranked.png',
    ossapi.enums.RankStatus.GRAVEYARD: 'data/rankedStatus/pending.png',
    ossapi.enums.RankStatus.PENDING: 'data/rankedStatus/pending.png',
    ossapi.enums.RankStatus.WIP: 'data/rankedStatus/pending.png',
    ossapi.enums.RankStatus.LOVED: 'data/rankedStatus/loved.png',
    ossapi.enums.RankStatus.APPROVED: 'data/rankedStatus/approved.png',
    ossapi.enums.RankStatus.QUALIFIED: 'data/rankedStatus/approved.png',
}

class RenderedReplay:
    title: str = None
    description: str = None
    thumbnail: bytes = None
    replayFileContent: bytes | None = None

def getTextLength(font: ImageFont, text: str) -> int:
    return font.getbbox(text)[2]


def getFont(size: int) -> ImageFont:
    return ImageFont.truetype('data/font/Aller_Bd.ttf', size)


def shortenSongTitle(songTitle: str) -> str:
    songTitle = songTitle.split('(feat.', 1)
    if len(songTitle) < 2:
        songTitle = songTitle[0].split('feat.', 1)
    if len(songTitle) > 1:
        rest = songTitle[1].split('(', 1)
        if len(rest) > 1:
            songTitle = songTitle[0] + '(' + rest[1]
    else:
        songTitle = songTitle[0]

    return songTitle


def add_corners(im: Image, rad: int) -> Image:
    # Copypasted LMAO
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)

    return im


def createThumbnail(user: User, score: Score, beatmap: Beatmap, description: str = '', shortenTitle: bool = False) -> bytes:
    beatmapset = beatmap.beatmapset()

    cover = requests.get(
        f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/card@2x.jpg?1650700167').content

    if user.statistics.global_rank is None:
        template = Image.open('data/templates/unranked.png', 'r').convert('RGBA')
    else:
        template = Image.open('data/templates/main.png', 'r').convert('RGBA')
    coverFile = io.BytesIO(cover)
    try:
        thumbnail = Image.open(coverFile)
    except:
        thumbnail = Image.open('data/background/default.jpg', 'r')
    enhancer = ImageEnhance.Brightness(thumbnail)
    thumbnail = enhancer.enhance(0.5)
    thumbnail = thumbnail.crop((130, 0, 670, 280))
    thumbnail = thumbnail.resize((1920, 1080))
    thumbnail = thumbnail.convert('RGBA')

    box = (0, 300, 1920, 1080)
    ic = thumbnail.crop(box)
    for i in range(10):
        ic = ic.filter(ImageFilter.BLUR)
        ic = ic.filter(ImageFilter.BLUR)
        ic = ic.filter(ImageFilter.BLUR)
    thumbnail.paste(ic, box)

    thumbnail.paste(template, (0, 0), template)

    pfpBytes = requests.get(f'https://a.ppy.sh/{user.id}?1692642160.jpeg').content

    pfpFile = io.BytesIO(pfpBytes)

    pfp = Image.open(pfpFile).resize((300, 300)).convert('RGBA')
    pfp = add_corners(pfp, 85)
    thumbnail.paste(pfp, (812, 443), pfp)

    thumbnail = thumbnail.convert('RGB')

    drawer = ImageDraw.Draw(thumbnail)
    combo = str(score.max_combo) + 'x'
    drawer.text((380 - 30 * len(combo), 255), combo, font=getFont(100), fill=(255, 255, 255), align='left')

    username = user.username
    x = (thumbnail.width - getTextLength(getFont(60), username)) // 2
    drawer.text((x, 278), username, font=getFont(60), fill=(255, 255, 255))
    acc = str(round(score.accuracy * 100, 2))
    if len(acc) > 5:
        acc += '0'
    acc += '%'
    x = (1550 - getTextLength(getFont(90), acc) // 2)
    drawer.text((x, 262), acc, font=getFont(90), fill=(255, 255, 255))

    if user.statistics.global_rank is not None:
        globalRank = '#' + str(user.statistics.global_rank)
        drawer.text((1293, 570), globalRank, font=getFont(65), fill=(255, 255, 255))

        swissRank = '#' + str(user.statistics.country_rank)
        drawer.text((1293, 662), swissRank, font=getFont(65), fill=(255, 255, 255))

    artist = beatmapset.artist
    x = (thumbnail.width - getTextLength(getFont(60), artist)) // 2
    drawer.text((x, 30), artist, font=getFont(60), fill=(222, 222, 222))

    songTitle = shortenSongTitle(beatmapset.title) if shortenTitle else beatmapset.title

    x = (thumbnail.width - getTextLength(getFont(70), songTitle)) // 2
    drawer.text((x, 120), songTitle, font=getFont(70), fill=(255, 255, 255))

    x = (thumbnail.width - getTextLength(getFont(70), description)) // 2
    drawer.text((x, 880), description, font=getFont(70), fill=(255, 255, 255))

    mods = modStringToList(handleModToString(score.mods))

    pp = None if score.pp is None else f"{int(score.pp)}pp"

    if score.pp is None:
        heart = Image.open('data/misc/heart.png').resize((150, 150))
        thumbnail.paste(heart, (1390, 390), heart)
    else:
        drawer.text((1260, 400), pp, font=getFont(100), fill=(255, 255, 255))

    avg = len(mods) / 2
    for id in range(len(mods)):
        if mods[id].lower() in ['cl', 'v2', 'nm']:
            continue
        mod = Image.open(f'data/mods/{mods[id].lower()}.png')
        mod = mod.resize((80, 56))
        thumbnail.paste(mod, (int(920 - 44 - 88 * (avg - id - 1)), 780), mod)

    rank = Image.open(f'data/rank/{score.rank.value}.png')

    rank = rank.resize((300, 300))

    thumbnail.paste(rank, (490, 450), rank)

    rankedStatus = Image.open(rankedAlias[beatmap.ranked])

    rankedStatus = rankedStatus.resize((130, 130))

    thumbnail.paste(rankedStatus, (30, 25), rankedStatus)

    gamemode = Image.open(f'data/gamemode/{beatmap.mode.value}.png')

    gamemode = gamemode.resize((130, 130))

    thumbnail.paste(gamemode, (1760, 25), gamemode)
    
    whatever = io.BytesIO()
    thumbnail.save(whatever, 'JPEG')
    thumbnail.close()

    return whatever.getvalue()



def createTitle(osu: ossapi.Ossapi, user: User, score: Score, beatmap: Beatmap, shortenTitle: bool = False) -> str:
    beatmapset = beatmap.beatmapset()
    songTitle = shortenSongTitle(beatmapset.title) if shortenTitle else beatmapset.title
    modString = handleModToString(score.mods)
    detailed: DifficultyAttributes = osu.beatmap_attributes(beatmap.id, mods=modString.replace('V2', ''))
    songInfo = f"{beatmapset.artist} - {songTitle}"
    mapInfo = f"[{beatmap.version}] {round(detailed.attributes.star_rating, 2)}⭐ +{modString}"
    return f'{user.username} | {songInfo}{mapInfo}'


def createDescription(user: User, score: Score, beatmap: Beatmap) -> str:
    scoreLink = f'https://osu.ppy.sh/scores/{score.id}'
    page = requests.get(scoreLink).text.replace('\n', '')
    if re.match('.*Page Missing.*', page):
        scoreLink = 'not on the website'

    return (
        f"This score was set on {score.ended_at.strftime('%d.%m.%Y at %H:%M')}.\n"
        f"\n"
        f"Player: https://osu.ppy.sh/users/{user.id}\n"
        f"Beatmap: https://osu.ppy.sh/beatmaps/{beatmap.id}\n"
        f"Score: {scoreLink}\n"
        f"\n"
        f"Join the osu swiss community in discord: https://discord.com/invite/SHz8QtD\n"
    )


def createReplayFile(osu: ossapi.Ossapi, score: Score) -> bytes|None:
    try:
        return osu.download_score(score.id, raw=True)
    except ValueError:
        return None

def createAll(osu: ossapi.Ossapi, user: User, score: Score, beatmap: Beatmap, description='',
              shortenTitle: bool = False) -> RenderedReplay:
    renderedReplay = RenderedReplay()
    renderedReplay.thumbnail = createThumbnail(user, score, beatmap, description, shortenTitle)
    renderedReplay.title = createTitle(osu, user, score, beatmap, shortenTitle)
    renderedReplay.description = createDescription(user, score, beatmap)
    renderedReplay.replayFileContent = createReplayFile(osu, score)
    return renderedReplay
