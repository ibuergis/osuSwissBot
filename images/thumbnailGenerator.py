import os
import re

import ossapi
from PIL import Image, ImageEnhance, ImageFont, ImageDraw, ImageFilter
from ossapi import User, Score, Beatmap
import requests
from ossapi.models import DifficultyAttributes


class ThumbnailGenerator:

    async def add_corners(self, im, rad) -> Image:
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

    def getTextLength(self, font, text):
        return font.getbbox(text)[2]

    async def createThumbnail(self, osu: ossapi.Ossapi, player: User, score: Score, beatmap: Beatmap, description='', shortenTitle: bool = False):
        beatmapset = beatmap.beatmapset()
        with open(f'images/temp/{score.best_id}.jpg', 'wb+') as f:
            cover = requests.get(f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/card@2x.jpg?1650700167').content
            f.write(cover)
            f.close()

        with open(f'images/temp/{score.best_id}.png', 'wb+') as f:
            cover = requests.get(f'https://a.ppy.sh/{player.id}?1692642160.jpeg').content
            f.write(cover)
            f.close()

        template = Image.open('images/templates/main.png', 'r').convert('RGBA')

        # 1 char is 60px width
        comboFont = ImageFont.truetype('images/font/Aller_Bd.ttf', 100)

        accFont = ImageFont.truetype('images/font/Aller_Bd.ttf', 90)

        rankFont = ImageFont.truetype('images/font/Aller_Bd.ttf', 65)

        titleFont = ImageFont.truetype('images/font/Aller_Bd.ttf', 70)

        userFont = ImageFont.truetype('images/font/Aller_Bd.ttf', 60)

        thumbnail = Image.open(f'images/temp/{score.best_id}.jpg')
        enhancer = ImageEnhance.Brightness(thumbnail)
        thumbnail = enhancer.enhance(0.5)
        thumbnail = thumbnail.crop((130, 0, 670, 280))
        thumbnail = thumbnail.resize((1920, 1080))
        thumbnail = thumbnail.convert('RGBA')

        box = (0, 300, 1920, 1080)
        ic = thumbnail.crop(box)
        for i in range(10):  # with the BLUR filter, you can blur a few times to get the effect you're seeking
            ic = ic.filter(ImageFilter.BLUR)
            ic = ic.filter(ImageFilter.BLUR)
            ic = ic.filter(ImageFilter.BLUR)
        thumbnail.paste(ic, box)

        thumbnail.paste(template, (0, 0), template)

        pfp = Image.open(f'images/temp/{score.best_id}.png').resize((300, 300)).convert('RGBA')
        pfp = await self.add_corners(pfp, 85)
        box = pfp.getbbox()
        width = box[2] - box[0]
        height = box[3] - box[1]
        x = (thumbnail.width - width) // 2
        y = (thumbnail.height - height) // 2
        thumbnail.paste(pfp, (812, 443), pfp)

        thumbnail = thumbnail.convert('RGB')

        drawer = ImageDraw.Draw(thumbnail)
        combo = str(score.max_combo) + 'x'
        drawer.text((380 - 30 * len(combo), 255), combo, font=comboFont, fill=(255, 255, 255), align='left')

        user = player.username
        x = (thumbnail.width - self.getTextLength(userFont, user)) // 2
        drawer.text((x, 278), user, font=userFont, fill=(255, 255, 255))
        acc = str(round(score.accuracy*100, 2))
        if len(acc) > 5:
            acc += '0'
        acc += '%'
        x = (1550 - self.getTextLength(accFont, acc) // 2)
        drawer.text((x, 262), acc, font=accFont, fill=(255, 255, 255))

        pp = None if score.pp is None else f"{int(score.pp)}pp"

        if score.pp is None:
            heart = Image.open('images/misc/heart.png').resize((150, 150))
            thumbnail.paste(heart, (1390, 390), heart)
        else:
            drawer.text((1260, 400), pp, font=comboFont, fill=(255, 255, 255))

        globalRank = '#' + str(player.statistics.global_rank)
        drawer.text((1293, 570), globalRank, font=rankFont, fill=(255, 255, 255))

        swissRank = '#' + str(player.statistics.country_rank)
        drawer.text((1293, 662), swissRank, font=rankFont, fill=(255, 255, 255))

        artist = beatmapset.artist
        x = (thumbnail.width - self.getTextLength(userFont, artist)) // 2
        drawer.text((x, 30), artist, font=userFont, fill=(222, 222, 222))

        songTitle = beatmapset.title

        if shortenTitle:
            songTitle = songTitle.split('(feat.', 1)
            if len(songTitle) < 2:
                songTitle = songTitle[0].split('feat.', 1)
            if len(songTitle) > 1:
                rest = songTitle[1].split('(', 1)
                if len(rest) > 1:
                    songTitle = songTitle[0] + '(' + rest[1]
            else:
                songTitle = songTitle[0]

        title = songTitle
        x = (thumbnail.width - self.getTextLength(titleFont, title)) // 2
        drawer.text((x, 120), title, font=titleFont, fill=(255, 255, 255))

        x = (thumbnail.width - self.getTextLength(titleFont, description)) // 2
        drawer.text((x, 880), description, font=titleFont, fill=(255, 255, 255))

        mod = score.mods.short_name()
        if mod == 'NM':
            mod = ''
        n = 2
        mods = [mod[i:i + n] for i in range(0, len(mod), n)]

        avg = len(mods) / 2
        for id in range(len(mods)):
            mod = Image.open(f'images/mods/{mods[id].lower()}.png')
            thumbnail.paste(mod, (int(920 - 44 - 88 * (avg - id - 1)), 780), mod)

        rank = Image.open(f'images/rank/{score.rank.value}.png')

        rank = rank.resize((300, 300))

        thumbnail.paste(rank, (490, 450), rank)

        thumbnail.save(f'images/output/{score.best_id}.jpg')

        description = open(f'images/output/{score.best_id}Description', 'w+')
        title = open(f'images/output/{score.best_id}Title', 'w+')

        detailed: DifficultyAttributes = await osu.beatmap_attributes(beatmap.id, mods=score.mods)
        title.write(f'{player.username} | {beatmapset.artist} - {songTitle}[{beatmap.version}] {round(detailed.attributes.star_rating, 2)}#star# +{score.mods.short_name()}')

        description.write(
            f"This score was set on {score.created_at.strftime('%d.%m.%Y at %H:%M')}.\n"
            f"\n"
            f"Player: https://osu.ppy.sh/users/{player.id}\n"
            f"Beatmap: https://osu.ppy.sh/beatmaps/{beatmap.id}\n"
            f"Score: https://osu.ppy.sh/scores/osu/{score.best_id}\n"
            f"\n"
            f"Join the osu swiss community in discord: https://discord.com/invite/SHz8QtD\n"
            f"\n"
            f"\n"
            f"This replay was rendered with: https://ordr.issou.best\n"
        )

        description.close()

        os.remove(f'images/temp/{score.best_id}.png')
        os.remove(f'images/temp/{score.best_id}.jpg')
