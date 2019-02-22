from dataclasses import dataclass


@dataclass
class File:
    id: int
    size: int = None


@dataclass
class Photo(File):
    width: int
    height: int


@dataclass
class Document(File):
    name: str = None


@dataclass
class Voice(File):
    duration: int


@dataclass
class VideoNote(Voice):
    length: int


@dataclass
class Audio(Voice):
    performer: str = None
    title: str = None


@dataclass
class Video(Voice):
    width: int
    height: int


@dataclass
class Animation(Video):
    name: str
