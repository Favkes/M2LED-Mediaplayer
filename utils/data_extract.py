from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, COMM
from PIL import Image, ImageTk
from io import BytesIO


# TODO: Add color palette extraction for automatic color-mapping
#       (could be in tools.py)


def grab_cover(mp3_path, size: tuple[int, int] = (550, 550)):
    audio = MP3(mp3_path, ID3=ID3)
    for tag in audio.tags.values():
        if isinstance(tag, APIC):
            image_data = BytesIO(tag.data)
            image = ImageTk.PhotoImage(
                Image.open(image_data).resize(size)
            )
            return image
    return None


def grab_duration(mp3_path):
    audio = MP3(mp3_path)
    return audio.info.length


def grab_name(mp3_path):
    audio = MP3(mp3_path, ID3=ID3)
    title_tag = audio.tags.get('TIT2')
    if title_tag: return title_tag
    return "-Untitled-"


def check_uuid(mp3_path) -> str | None:
    audio = MP3(mp3_path, ID3=ID3)
    try:
        return audio.tags['uuid']
    except KeyError:
        return None


def add_uuid(mp3_path, uuid: str) -> None:
    audio = MP3(mp3_path, ID3=ID3)

    # Ensuring .tags is not None
    if audio.tags is None:
        audio.add_tags()

    audio.tags.add(
        COMM(encoding=3, lang='eng', desc='uuid', text=uuid)
    )
    audio.save()
