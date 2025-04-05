from __future__ import annotations

import datetime
import numpy
import typing
import pickle
import zlib

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem

import Resume


class MyEmployeeProfile:
    """
    Basic class holding employee profile information
    """

    EMPLOYEES: dict[int, MyEmployeeProfile] = {}
    __LOADED__: bool = False

    @staticmethod
    def load(root_dir: str) -> int:
        """
        Loads all employee profiles in the specified directory
        :param root_dir: The directory to load from
        :return: The number of loaded employee profiles
        """

        if MyEmployeeProfile.__LOADED__:
            return 0

        root_dir: FileSystem.Directory = FileSystem.Directory(root_dir)
        dirs: list[FileSystem.Directory] = [root_dir]

        while len(dirs) > 0:
            base_dir: FileSystem.Directory = dirs.pop(0)

            if not base_dir.exists():
                continue

            dirs.extend(base_dir.dirs())

            for file in base_dir.files():
                if file.extension() != 'kvp':
                    continue

                with file.open('r') as fstream:
                    index: int = int(file.filename())
                    offset: str = file.filepath()[len(root_dir.dirpath()):]
                    MyEmployeeProfile.EMPLOYEES[index] = MyEmployeeProfile(offset, KVP.KVP.decode(fstream.read()))

        MyEmployeeProfile.__LOADED__ = True
        return len(MyEmployeeProfile.EMPLOYEES)

    @staticmethod
    def save(root_dir: str) -> None:
        """
        Saves all company roles to the specified directory
        :param root_dir: The directory to save to
        :return: NONE
        """

        root_dir: FileSystem.Directory = FileSystem.Directory(root_dir)

        if not root_dir.exists():
            root_dir.create()

        for uid, role in MyEmployeeProfile.EMPLOYEES.items():
            role_file: FileSystem.File = root_dir.file(role.__file_offset__)
            parent: FileSystem.Directory = role_file.parentdir()

            if not parent.exists():
                parent.create()

            with role_file.open('w') as fstream:
                fstream.write(role.to_kvp().encode(True))

    @staticmethod
    def get_employees_by_name(name: str) -> tuple[MyEmployeeProfile, ...]:
        """
        Gets all employees with the specified name
        :param name: The employee name
        :return: All matching employees
        """

        return tuple(profile for profile in MyEmployeeProfile.EMPLOYEES.values() if profile.name == name)

    def __init__(self, file_offset: str, kvp: KVP.KVP):
        """
        [Constructor] - Creates a new employee profile
        This will not add it to the internal listing and should not be called explicitly
        :param file_offset: The relative path of this file relative to the root directory
        :param kvp: The employee profile's KVP information
        """

        self.__file_offset__: str = str(file_offset)
        self.__employee_name__: str = str(kvp.EmployeeProfile.Name[0])
        self.__skills__: list[str] = [str(x) for x in kvp.EmployeeProfile.Skills]
        self.__project_ids__: list[int] = [int(x) for x in kvp.EmployeeProfile.ProjectIDs]
        self.__performance_review_ids__: list[int] = [int(x) for x in kvp.EmployeeProfile.PerfReviewIDs]
        self.__assessment_ids: list[int] = [int(x) for x in kvp.EmployeeProfile.AssessmentIDs]
        self.__roles__: list[str] = [str(x) for x in kvp.EmployeeProfile.CurrentRole]

        if len(kvp.EmployeeProfile.ResumeID) == 3:
            self.__resume_batch_id__: slice = slice(int(kvp.EmployeeProfile.ResumeID[0]), int(kvp.EmployeeProfile.ResumeID[1]))
            self.__resume_file_id__: int = int(kvp.EmployeeProfile.ResumeID[2])
        else:
            self.__resume_batch_id__: slice = slice(-1, -1)
            self.__resume_file_id__: int = -1

        self.__start_date__: datetime.datetime = datetime.datetime.fromtimestamp(0 if len(kvp.EmployeeProfile.StartDate) == 0 else float(kvp.EmployeeProfile.StartDate[0]), datetime.timezone.utc)
        self.__image__: numpy.ndarray = numpy.full((512, 512, 4), 0, numpy.uint8) if len(kvp.EmployeeProfile.Image) == 0 else numpy.reshape(numpy.frombuffer(zlib.decompress(kvp.EmployeeProfile.Image[0]), dtype=numpy.uint8), (512, 512, 4))
        self.__extra_meta__: typing.Any = None if len(kvp.EmployeeProfile.Extra) == 0 else pickle.loads(kvp.EmployeeProfile.Extra[0])
        self.__bio__: str = '' if len(kvp.EmployeeProfile.Bio) == 0 else zlib.decompress(kvp.EmployeeProfile.Bio[0]).decode()
        self.__digital_portfolio__: dict[str, str] = {str(website): str(url) for website, url in kvp.EmployeeProfile.DigitalPortfolio}

    def to_kvp(self) -> KVP.KVP:
        """
        Converts this object to KVP for saving
        :return: A KVP object
        """

        mapping: dict = {
            'EmployeeProfile': {
                'Name': [self.__employee_name__],
                'Skills': self.__skills__,
                'ProjectIDs': self.__project_ids__,
                'PerfReviewIDs': self.__performance_review_ids__,
                'AssessmentIDs': self.__assessment_ids,
                'CurrentRole': self.__roles__,
                'ResumeID': [] if self.resume is None else [self.__resume_batch_id__.start, self.__resume_batch_id__.stop, self.__resume_file_id__],
                'StartDate': [self.__start_date__.timestamp()],
                'Image': [zlib.compress(self.__image__.tobytes(), zlib.Z_BEST_COMPRESSION)],
                'Extra': [] if self.__extra_meta__ is None else [pickle.dumps(self.__extra_meta__)],
                'Bio': [zlib.compress(self.__bio__.encode())],
                'DigitalPortfolio': {website: [url] for website, url in self.__digital_portfolio__.items()}
            }
        }
        return KVP.KVP(None, mapping)

    @property
    def name(self) -> str:
        """
        Gets this employee's name
        :return: This employee's name
        """

        return self.__employee_name__

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets this employee's name
        :param name: The new name, must be a string at least 2 characters long
        :return: NONE
        """

        assert isinstance(name, str) and len(name) >= 2, 'Invalid name'
        self.__employee_name__ = name

    @property
    def skills(self) -> tuple[str, ...]:
        """
        Gets this employee's skills
        :return: This employee's skills
        """

        return tuple(self.__skills__)

    @property
    def resume(self) -> Resume.MyResume | None:
        """
        Gets this employee's resume
        :return: This employee's resume or None
        """

        return Resume.MyResume.get_resume(self.__resume_batch_id__, self.__resume_file_id__)

    @property
    def current_roles(self) -> tuple[str, ...]:
        """
        Gets this employee's current role(s)
        :return: This employee's current role(s)
        """

        return tuple(self.__roles__)

    @property
    def image_icon(self) -> numpy.ndarray:
        """
        Gets this employee's icon image
        :return: This employee's icon image
        """

        return self.__image__.copy()

    @property
    def bio(self) -> str:
        """
        Gets this employee's bio
        :return: This employee's bio
        """

        return self.__bio__

    @property
    def metadata(self) -> typing.Any:
        """
        Gets this employee's extra metadata
        :return: This employee's extra metadata
        """

        return self.__extra_meta__
