class Emotion:
    sad: float
    angry: float
    surprise: float
    fear: float
    happy: float
    disgust: float
    neutral: float

    def __init__(self, from_api) -> None:
        self.sad = from_api['sad']
        self.angry = from_api['angry']
        self.surprise = from_api['surprise']
        self.fear = from_api['fear']
        self.happy = from_api['happy']
        self.disgust = from_api['disgust']
        self.neutral = from_api['neutral']


class Race:
    indian: float
    asian: float
    latino_hispanic: float
    black: float
    middle_eastern: float
    white: float

    def __init__(self, from_api) -> None:
        self.indian = from_api['indian']
        self.asian = from_api['asian']
        self.latino_hispanic = from_api['latino_hispanic']
        self.black = from_api['black']
        self.middle_eastern = from_api['middle_eastern']
        self.white = from_api['white']


class Region:
    x: int
    y: int
    w: int
    h: int

    def __init__(self, from_api) -> None:
        i = 0
        for index in ['x', 'y', 'w', 'h']:
            setattr(self, index, from_api[i])
            i = i + 1


class DeepFaceResult:
    region: Region
    age: float
    gender: str
    dominant_emotion: str
    emotion: Emotion
    dominant_race: str
    race: Race

    def __del__(self):
        self.frame = None
        self.region = None
        self.dominant_emotion = None
        self.emotion = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.frame is not None:
            del self.frame
        self.region = None
        self.dominant_emotion = None
        self.emotion = None
        return self

    def __init__(self, from_api) -> None:
        self.frame = from_api['frame']
        self.region = Region(from_api['region'])
        self.dominant_emotion = from_api['dominant_emotion']
        self.emotion = Emotion(from_api['emotion'])
