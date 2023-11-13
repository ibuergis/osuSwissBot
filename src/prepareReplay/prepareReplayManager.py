import requests

import os
import re

import ossapi
from ossapi import User, Score, Beatmap
from ossapi.models import DifficultyAttributes

from PIL import Image, ImageEnhance, ImageFont, ImageDraw, ImageFilter


def getTextLength(font, text):
    return font.getbbox(text)[2]


def getFont(size) -> ImageFont:
    return ImageFont.truetype('data/font/Aller_Bd.ttf', size)


async def shortenSongTitle(songTitle: str):
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


async def add_corners(im, rad) -> Image:
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


async def createThumbnail(user: User, score: Score, beatmap: Beatmap, description='', shortenTitle: bool = False):
    beatmapset = beatmap.beatmapset()

    with open(f'data/temp/{score.best_id}.jpg', 'wb+') as f:
        cover = requests.get(
            f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/card@2x.jpg?1650700167').content
        f.write(cover)
        f.close()

    with open(f'data/temp/{score.best_id}.png', 'wb+') as f:
        cover = requests.get(f'https://a.ppy.sh/{user.id}?1692642160.jpeg').content
        f.write(cover)
        f.close()

    template = Image.open('data/templates/main.png', 'r').convert('RGBA')
    thumbnail = Image.open(f'data/temp/{score.best_id}.jpg')
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

    pfp = Image.open(f'data/temp/{score.best_id}.png').resize((300, 300)).convert('RGBA')
    pfp = await add_corners(pfp, 85)
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

    pp = None if score.pp is None else f"{int(score.pp)}pp"

    if score.pp is None:
        heart = Image.open('data/misc/heart.png').resize((150, 150))
        thumbnail.paste(heart, (1390, 390), heart)
    else:
        drawer.text((1260, 400), pp, font=getFont(100), fill=(255, 255, 255))

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

    mod = score.mods.short_name()
    if mod == 'NM':
        mod = ''
    n = 2
    mods = [mod[i:i + n] for i in range(0, len(mod), n)]

    avg = len(mods) / 2
    for id in range(len(mods)):
        mod = Image.open(f'data/mods/{mods[id].lower()}.png')
        thumbnail.paste(mod, (int(920 - 44 - 88 * (avg - id - 1)), 780), mod)

    rank = Image.open(f'data/rank/{score.rank.value}.png')

    rank = rank.resize((300, 300))

    thumbnail.paste(rank, (490, 450), rank)

    thumbnail.save(f'data/output/{score.best_id}.jpg')


async def createTitle(osu: ossapi.OssapiAsync, user: User, score: Score, beatmap: Beatmap, shortenTitle: bool = False):
    beatmapset = beatmap.beatmapset()
    songTitle = shortenSongTitle(beatmapset.title) if shortenTitle else beatmapset.title
    detailed: DifficultyAttributes = await osu.beatmap_attributes(beatmap.id, mods=score.mods)
    title = open(f'data/output/{score.best_id}Title', 'w+')
    title.write(
        f'{user.username} | {beatmapset.artist} - {songTitle}[{beatmap.version}] {round(detailed.attributes.star_rating, 2)}#star# +{score.mods.short_name()}')
    title.close()


async def createDescription(user: User, score: Score, beatmap: Beatmap):
    scoreLink = f'https://osu.ppy.sh/scores/osu/{score.best_id}'
    page = requests.get(scoreLink).text.replace('\n', '')
    if re.match('.*Page Missing.*', page):
        scoreLink = 'not on the website'

    description = open(f'data/output/{score.best_id}Description', 'w+')
    description.write(
        f"This score was set on {score.created_at.strftime('%d.%m.%Y at %H:%M')}.\n"
        f"\n"
        f"Player: https://osu.ppy.sh/users/{user.id}\n"
        f"Beatmap: https://osu.ppy.sh/beatmaps/{beatmap.id}\n"
        f"Score: {scoreLink}\n"
        f"\n"
        f"Join the osu swiss community in discord: https://discord.com/invite/SHz8QtD\n"
    )
    description.close()


async def createReplayFile(osu: ossapi.OssapiAsync, score: Score,
                           gamemode: ossapi.GameMode = ossapi.GameMode.OSU) -> bool:
    try:
        replay = await osu.download_score(gamemode, score.best_id, raw=True)
        with open(f'data/output/{score.best_id}.osr', 'wb+') as f:
            f.write(replay)
            f.close()
            return True
    except ValueError:
        return False


async def createAll(osu: ossapi.OssapiAsync, user: User, score: Score, beatmap: Beatmap, description='',
                    shortenTitle: bool = False) -> bool:
    await createThumbnail(user, score, beatmap, description, shortenTitle)
    await createTitle(osu, user, score, beatmap, shortenTitle)
    await createDescription(user, score, beatmap)
    return await createReplayFile(osu, score, score.mode)


def cleanup(scoreId: int):
    os.remove(f'data/temp/{scoreId}.png')
    os.remove(f'data/temp/{scoreId}.jpg')
    os.remove(f'data/output/{scoreId}Description')
    os.remove(f'data/output/{scoreId}Title')
    os.remove(f'data/output/{scoreId}.jpg')
    try:
        os.remove(f'data/output/{scoreId}.osr')
    except FileNotFoundError:
        pass
