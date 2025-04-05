from __future__ import annotations

import numpy
import typing
import pickle

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

        dirs: list[FileSystem.Directory] = [FileSystem.Directory(root_dir)]

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
                    MyEmployeeProfile.EMPLOYEES[index] = MyEmployeeProfile(KVP.KVP.decode(fstream.read()))

        MyEmployeeProfile.__LOADED__ = True
        return len(MyEmployeeProfile.EMPLOYEES)

    @staticmethod
    def get_employees_by_name(name: str) -> tuple[MyEmployeeProfile, ...]:
        """
        Gets all employees with the specified name
        :param name: The employee name
        :return: All matching employees
        """

        return tuple(profile for profile in MyEmployeeProfile.EMPLOYEES.values() if profile.name == name)

    def __init__(self, kvp: KVP.KVP):
        """
        [Constructor] - Creates a new employee profile
        This will not add it to the internal listing and should not be called explicitly
        :param kvp: The employee profile's KVP information
        """

        self.__employee_name__: str = kvp.EmployeeProfile.Name[0]
        self.__skills__: list[str] = kvp.EmployeeProfile.Skills
        self.__project_ids__: list[int] = [int(x) for x in kvp.EmployeeProfile.ProjectIDs]
        self.__performance_review_ids__: list[int] = [int(x) for x in kvp.EmployeeProfile.PerfReviewIDs]
        self.__assessment_ids: list[int] = [int(x) for x in kvp.EmployeeProfile.AssessmentIDs]
        self.__roles__: list[str] = list(kvp.EmployeeProfile.CurrentRole)

        if len(kvp.EmployeeProfile.ResumeID) == 3:
            self.__resume_batch_id__: slice = slice(kvp.EmployeeProfile.ResumeID[0], kvp.EmployeeProfile.ResumeID[1])
            self.__resume_file_id__: int = kvp.EmployeeProfile.ResumeID[2]
        else:
            self.__resume_batch_id__: slice = slice(-1, -1)
            self.__resume_file_id__: int = -1

        self.__image__: numpy.ndarray = numpy.full((512, 512, 4), 0, numpy.uint8) if len(kvp.EmployeeProfile.Image) == 0 else numpy.frombuffer(kvp.EmployeeProfile.Image[0], dtype=numpy.uint8)
        self.__extra_meta__: typing.Any = None if len(kvp.EmployeeProfile.Extra) == 0 else pickle.loads(kvp.EmployeeProfile.Extra[0])
        self.__bio__: str = '' if len(kvp.EmployeeProfile.Bio) == 0 else kvp.EmployeeProfile.Bio[0]

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
