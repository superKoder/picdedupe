from picdeduper import common as pdc
from picdeduper import platform as pds
from picdeduper.bimap import BiMap
from picdeduper import time as pdt

from abc import ABC, abstractmethod
from typing import List, Dict


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


class FixItDescriptionDangerousTextElement(FixItDescriptionBoldTextElement):
    """Stronger than bold!"""
    pass


class FixItDescriptionValueElement(FixItDescriptionElement):
    def has_link(self) -> bool:
        return False

    def get_link(self) -> str:
        return None


class FixItDescriptionFilePathElement(FixItDescriptionValueElement):
    def __init__(self, path: pds.Path, label: str = None) -> None:
        super().__init__(path)
        self.path = path
        self.label = label or path

    def has_link(self) -> bool:
        return True

    def get_link(self) -> str:
        return pds.file_link_for_path(self.path)

    def get_label(self) -> str:
        return self.label


class FixItDescription:
    def __init__(self) -> None:
        self.elements: List[FixItDescriptionElement] = list()

    def add(self, element: FixItDescriptionElement):
        self.elements.append(element)

    def clear(self):
        self.elements.clear()

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

    @abstractmethod
    def leave_txt_history(self, txt_content: str) -> None:
        pass


class BasePlatformFixItAction(FixItAction):
    """Abstract base class for FixItActions that rely on Platform"""

    def __init__(self, platform: pds.Platform) -> None:
        super().__init__()
        self.platform = platform
        assert self.platform.is_mac_os()
        self.txt_path: pds.Path = None

    def set_txt_history_path(self, txt_path: pds.Path) -> None:
        self.txt_path = txt_path
        if pds.filename_ext(self.txt_path) != ".txt":
            self.txt_path += ".txt"

    def leave_txt_history(self, txt_content: str) -> None:
        if self.txt_path:
            assert pds.filename_ext(self.txt_path) == ".txt"
            txt_content += "\n" + self.description.as_simple_text() + "\n"
            self.platform.write_text_file(self.txt_path, txt_content)


class DoNothingAction(FixItAction):

    def __init__(self) -> None:
        super().__init__()
        self.description.add(FixItDescriptionTextElement("Do"))
        self.description.add(FixItDescriptionBoldTextElement("nothing"))

    def do_it(self) -> bool:
        pass

    def leave_txt_history(self, txt_content: str) -> None:
        pass


class FixItMoveFileAction(BasePlatformFixItAction):
    """Moves a file to another location"""

    def __init__(self, platform: pds.Platform, path: pds.Path, to_dir: pds.Path) -> None:
        super().__init__(platform)
        self.from_path = path
        self.to_dir = to_dir
        assert platform.path_exists(self.from_path)
        self.description.add(FixItDescriptionBoldTextElement("Move"))
        self.description.add(FixItDescriptionFilePathElement(path))
        self.description.add(FixItDescriptionTextElement("to directory"))
        self.description.add(FixItDescriptionFilePathElement(to_dir))

    def do_it(self, add_explanation=True) -> bool:
        assert self.platform.path_exists(self.from_path)
        self.platform.make_sure_path_exists(self.to_dir)
        assert self.platform.path_exists(self.to_dir)
        to_path = pds.path_join(self.to_dir, pds.path_filename(self.from_path))
        self.set_txt_history_path(to_path + ".txt")
        cmd = ["mv", self.from_path, self.to_dir]   # [!DFSO!]
        self.platform.stdout_of(cmd)


class FixItSoftDeleteFileAction(FixItMoveFileAction):
    """Delete a file (by moving it to some folder)"""

    def __init__(self, platform: pds.Platform, path: pds.Path, trash_dir: pds.Path) -> None:
        super().__init__(platform, path, trash_dir)
        assert platform.path_exists(self.from_path)
        self.description.clear()
        self.description.add(FixItDescriptionDangerousTextElement("Delete"))
        self.description.add(FixItDescriptionFilePathElement(self.from_path))
        self.description.add(FixItDescriptionTextElement("(by moving it to"))
        self.description.add(FixItDescriptionFilePathElement(self.to_dir))
        self.description.add(FixItDescriptionTextElement(")"))


class ChangeFileMTimeAction(BasePlatformFixItAction):
    """Changes the mtime of a file"""

    def __init__(self, platform: pds.Platform, path: pds.Path, ts: pdt.Timestamp) -> None:
        super().__init__(platform)
        self.path = path
        self.timestamp = ts
        assert platform.path_exists(self.path)
        self.description.clear()
        self.description.add(FixItDescriptionDangerousTextElement("Update mtime"))
        self.description.add(FixItDescriptionTextElement("of"))
        self.description.add(FixItDescriptionFilePathElement(self.path))
        self.description.add(FixItDescriptionTextElement("to"))
        self.description.add(FixItDescriptionValueElement(pdt.string_from_timestamp(ts)))

    def do_it(self) -> bool:
        assert self.platform.path_exists(self.path)
        self.platform.set_mtime(self.path, self.timestamp)
        self.set_txt_history_path(self.path + ".txt")


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
    def __init__(self, platform: pds.Platform, candidate_path: pds.Path, other_paths: pds.PathSet) -> None:
        super().__init__()
        self.description.add(FixItDescriptionTextElement("Detected an"))
        self.description.add(FixItDescriptionBoldTextElement("exact dupe"))
        self.description.add(FixItDescriptionTextElement("at"))
        self.description.add(FixItDescriptionFilePathElement(candidate_path))
        self.description.add(FixItDescriptionTextElement("matching"))
        for other_path in other_paths:
            self.description.add(FixItDescriptionFilePathElement(other_path))
        self.actions.append(FixItSoftDeleteFileAction(platform, candidate_path, "./_dupes"))
        self.actions.append(DoNothingAction())


class WrongFileTimeFixIt(FixIt):

    def __init__(self, platform: pds.Platform, path: pds.Path, file_ts: pdt.Timestamp, image_ts: pdt.Timestamp) -> None:
        super().__init__()
        self.description.add(FixItDescriptionTextElement("Inconsistent times"))
        self.description.add(FixItDescriptionTextElement("at"))
        self.description.add(FixItDescriptionFilePathElement(path))
        self.description.add(FixItDescriptionTextElement("(image:"))
        self.description.add(FixItDescriptionValueElement(pdt.string_from_timestamp(file_ts)))
        self.description.add(FixItDescriptionTextElement("!= file:"))
        self.description.add(FixItDescriptionValueElement(pdt.string_from_timestamp(image_ts)))
        self.description.add(FixItDescriptionTextElement(")"))
        self.actions.append(ChangeFileMTimeAction(platform, path, image_ts))
        self.actions.append(DoNothingAction())


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
    KEYB_KEY_FOR_ACTION_TYPE = BiMap({
        FixItSoftDeleteFileAction: "D",
        ChangeFileMTimeAction: "F",
        DoNothingAction: "",
    })

    FixitConfig = Dict[type, type]

    def __init__(self) -> None:
        super().__init__()
        self.key_action_binding: Dict[type, FixItAction] = dict()
        self.defaults: CommandLineFixItProcessor.FixitConfig = dict()

    def _keyb_key_for_action_type(self, action_type: type, pos: int) -> str:
        if action_type in type(self).KEYB_KEY_FOR_ACTION_TYPE:
            return type(self).KEYB_KEY_FOR_ACTION_TYPE[action_type]
        return str(pos)

    def _action_type_for_keyb_key(self, keyb_key: str) -> type:
        if not keyb_key in type(self).KEYB_KEY_FOR_ACTION_TYPE:
            return None
        return type(self).KEYB_KEY_FOR_ACTION_TYPE[keyb_key]

    def _keyb_key_for_action(self, action: FixItAction, pos: int) -> str:
        action_type = type(action)
        keyb_key = self._keyb_key_for_action_type(action_type, pos)
        self.key_action_binding[keyb_key] = action
        return keyb_key

    def _action_for_keyb_key(self, keyb_key: str) -> FixItAction:
        if not keyb_key in self.key_action_binding:
            return None
        return self.key_action_binding[keyb_key]

    def _reset_keyb_binding(self) -> None:
        self.key_action_binding.clear()

    def _pretty_keyb_key(self, keyb_key: str) -> str:
        if keyb_key == "":
            return "   ⏎ "
        if len(keyb_key) == 1:
            return f" {pds.Style.highlight(keyb_key.upper())} ⏎ "
        return keyb_key + " ⏎"

    def _pretty_description_element(self, element: FixItDescriptionElement) -> str:
        txt = element.get_text()
        if type(element) == FixItDescriptionBoldTextElement:
            return pds.Style.bold(txt.upper())
        if type(element) == FixItDescriptionFilePathElement:
            return pds.Style.link(element.get_link())
        if type(element) == FixItDescriptionDangerousTextElement:
            return pds.Style.attention(txt)
        if type(element) == FixItDescriptionValueElement:
            return pds.Style.highlight(txt)
        return txt

    def _pretty_description(self, description: FixItDescription) -> str:
        return " ".join([self._pretty_description_element(x)
                         for x in description.elements])

    def configure_fixit_default_actions(self, fixit_type: type, fixit_action_type: type):
        self.defaults[fixit_type] = fixit_action_type

    def process(self, fixit: FixIt) -> bool:
        self._reset_keyb_binding()
        description_text = self._pretty_description(fixit.describe())
        print("-- -- -- -- -- -- -- -- -- -- -- --")
        print(f"FIXIT: {description_text}")
        pos = 0
        chosen_action = None
        fixit_type = type(fixit)
        default_action_type = self.defaults[fixit_type] if (fixit_type in self.defaults) else None
        for action in fixit.get_proposed_actions():
            pos += 1
            keyb_key = self._keyb_key_for_action(action, pos)
            print(f" {self._pretty_keyb_key(keyb_key)} : {self._pretty_description(action.describe())}")
            if type(action) == default_action_type:
                print("Auto-selected!")
                chosen_action = action

        while not chosen_action:
            chosen_action = self._action_for_keyb_key(input("Your choice: ").upper())
        print(f"You picked: {self._pretty_description(chosen_action.describe())}")
        chosen_action.do_it()
        chosen_action.leave_txt_history(fixit.describe().as_simple_text())
        print("-- -- -- -- -- -- -- -- -- -- -- --")
        return True  # TODO
