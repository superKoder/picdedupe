from picdeduper import common as pdc
from picdeduper import platform as pds

from abc import ABC, abstractmethod
from typing import List


class FixItDescriptionElement(ABC):
    def __init__(self, text: str) -> None:
        self.text = text

    def get_text(self) -> str:
        return self.text

    @abstractmethod
    def has_link(self) -> bool:
        pass

    @abstractmethod
    def get_link(self) -> str:
        pass

class FixItDescriptionTextElement(FixItDescriptionElement):
    def has_link(self) -> bool:
        return False

    def get_link(self) -> str:
        return None


class FixItDescriptionBoldTextElement(FixItDescriptionElement):
    def has_link(self) -> bool:
        return False

    def get_link(self) -> str:
        return None


class FixItDescriptionFilePathElement(FixItDescriptionElement):
    def __init__(self, path: pds.Path, label: str = None) -> None:
        super().__init__(path)
        self.path = path
        self.label = label or path

    def has_link(self) -> bool:
        return True

    def get_link(self) -> str:
        return "file://" + self.path

    def get_label(self) -> str:
        return self.label


class FixItDescription:
    def __init__(self) -> None:
        self.elements: List[FixItDescriptionElement] = list()

    def add(self, element: FixItDescriptionElement):
        self.elements.append(element)
    # def add_text(self, text: str):
    #     self.add(FixItDescriptionTextElement(text))
    # def add_bold_text(self, text: str):
    #     self.add(FixItDescriptionBoldTextElement(text))
    # def add_file_path(self, path: pds.Path, label: str):
    #     self.add(FixItDescriptionFilePathElement(path, label))

    def as_simple_text(self) -> str:
        return " ".join([x.get_text() for x in self.elements])


class FixItAction(ABC):
    def __init__(self) -> None:
        self.description = FixItDescription()

    def describe(self) -> FixItDescription:
        return self.description

    @abstractmethod
    def do_it(self) -> bool:
        pass


class DoNothingAction(FixItAction):

    def __init__(self) -> None:
        super().__init__()
        self.description.add(FixItDescriptionTextElement("Do"))
        self.description.add(FixItDescriptionBoldTextElement("nothing"))

    def do_it(self) -> bool:
        pass


class FixItMoveFileAction(FixItAction):
    """Moves a file to another location"""

    def __init__(self, path: pds.Path, to_dir: pds.Path) -> None:
        super().__init__()
        self.path = path
        self.to_dir = to_dir
        self.description.add(FixItDescriptionBoldTextElement("Move"))
        self.description.add(FixItDescriptionFilePathElement(path))
        self.description.add(FixItDescriptionTextElement("to directory"))
        self.description.add(FixItDescriptionFilePathElement(to_dir))

    def do_it(self, add_explanation=True) -> bool:
        from_path = pds.path_join(self.from_dir, self.filename)
        to_path = pds.path_join(self.to_dir, self.filename)
        cmd = ["echo", "mv", from_path, to_path]
        pds.stdout_of(cmd)


class FixIt(ABC):
    def __init__(self) -> None:
        self.description = FixItDescription()
        self.actions = list()

    def describe(self) -> FixItDescription:
        return self.description

    def get_proposed_actions(self) -> List[FixItAction]:
        return self.actions

    # def ignore(self) -> None:
    #     pass # abstract


class ExactDupeFixIt(FixIt):
    def __init__(self, candidate_path: pds.Path, other_paths: pds.PathSet) -> None:
        super().__init__()
        self.description.add(FixItDescriptionTextElement("Detected an"))
        self.description.add(FixItDescriptionBoldTextElement("exact dupe"))
        self.description.add(FixItDescriptionTextElement("at"))
        self.description.add(FixItDescriptionFilePathElement(candidate_path))
        self.description.add(FixItDescriptionTextElement("matching"))
        for other_path in other_paths:
            self.description.add(FixItDescriptionFilePathElement(other_path))
        self.actions.append(FixItMoveFileAction(candidate_path, "./_dupes"))
        self.actions.append(DoNothingAction())


class WrongDateFixIt(FixIt):
    pass


class SimilarImageFixIt(FixIt):
    pass


class BetterQualityVersionFixIt(SimilarImageFixIt):
    """e.g. Found a new HEIC of a JPEG"""
    pass


class WorseQualityVersionFixIt(SimilarImageFixIt):
    """e.g. Found a new JPEG of an HEIC"""
    pass


class SmallerVersionFixIt(SimilarImageFixIt):
    """e.g. A cropped version of an original"""
    pass


class BiggerVersionFixIt(SimilarImageFixIt):
    """e.g. A cropped version of an original"""
    pass


class FixItProcessor(ABC):
    """
    The interface for any class that will receive FixIts and somehow
    make the decision of what FixItAction to execute. This could be 
    done by simply asking the User.
    """
    @abstractmethod
    def process(self, fixit: FixIt) -> bool:
        """Return True only if successfully processed"""
        pass


class CommandLineFixItProcessor(FixItProcessor):
    """
    Concrete FixItProcessor that interrupts the process to ask the User
    on the command line.
    """

    def keyb_key_for_action_type(self, action_type: type, pos: int) -> str:
        KEYB_KEY_FOR_ACTION_TYPE = {
            FixItMoveFileAction  : "  M  ",
            DoNothingAction      : " Esc ",
        }
        if action_type in KEYB_KEY_FOR_ACTION_TYPE:
            return KEYB_KEY_FOR_ACTION_TYPE[action_type]
        return pos

    def keyb_key_for_action(self, action: FixItAction, pos: int) -> str:
        return self.keyb_key_for_action_type(type(action), pos)

    def process(self, fixit: FixIt) -> bool:
        description_text = fixit.describe().as_simple_text()
        print("-- -- -- -- -- -- -- -- -- -- -- --")
        print(f"FIXIT: {description_text}")
        pos = 0
        for action in fixit.get_proposed_actions():
            pos += 1
            keyb_key = self.keyb_key_for_action(action, pos)
            print(f" <{keyb_key}> {action.describe().as_simple_text()}")
        print("-- -- -- -- -- -- -- -- -- -- -- --")
        return True # TODO
