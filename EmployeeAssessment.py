from __future__ import annotations

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem

import EmployeeProfile


class MyEmployeeAssessment:
    """
    Basic class holding employee assessment
    """

    ASSESSMENTS: dict[int, MyEmployeeAssessment] = {}
    __LOADED__: bool = False

    @staticmethod
    def load(root_dir: str) -> int:
        """
        Loads all employee assessments in the specified directory
        :param root_dir: The directory to load from
        :return: The number of loaded employee assessments
        """

        if MyEmployeeAssessment.__LOADED__:
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
                    MyEmployeeAssessment.ASSESSMENTS[index] = MyEmployeeAssessment(offset, KVP.KVP.decode(fstream.read()))

        MyEmployeeAssessment.__LOADED__ = True
        return len(MyEmployeeAssessment.ASSESSMENTS)

    @staticmethod
    def save(root_dir: str) -> None:
        """
        Saves all employee assessments to the specified directory
        :param root_dir: The directory to save to
        :return: NONE
        """

        root_dir: FileSystem.Directory = FileSystem.Directory(root_dir)

        if not root_dir.exists():
            root_dir.create()

        for uid, role in MyEmployeeAssessment.ASSESSMENTS.items():
            role_file: FileSystem.File = root_dir.file(role.__file_offset__)
            parent: FileSystem.Directory = role_file.parentdir()

            if not parent.exists():
                parent.create()

            with role_file.open('w') as fstream:
                fstream.write(role.to_kvp().encode(True))

    def __init__(self, file_offset: str, kvp: KVP.KVP):
        """
        [Constructor] - Creates a new employee assessment
        This will not add it to the internal listing and should not be called explicitly
        :param file_offset: The relative path of this file relative to the root directory
        :param kvp: The employee assessment's KVP information
        """

        self.__file_offset__: str = str(file_offset)
        self.__employee_id__: int = int(kvp.EmployeeAssessment.EmployeeID[0])
        self.__categories__: dict[str, float] = {str(category): float(rating[0]) for category, rating in kvp.EmployeeAssessment.Categories}

    def to_kvp(self) -> KVP.KVP:
        """
        Converts this object to KVP for saving
        :return: A KVP object
        """

        mapping: dict = {
            'EmployeeAssessment': {
                'EmployeeID': [self.__employee_id__],
                'Categories': {category: [rating] for category, rating in self.__categories__.items()}
            }
        }
        return KVP.KVP(None, mapping)

    @property
    def employee_id(self) -> int:
        """
        :return: The associated employee ID
        """

        return self.__employee_id__

    @property
    def employee(self) -> EmployeeProfile.MyEmployeeProfile | None:
        """
        Gets the employee profile associated with this assessment
        :return: The employee profile
        """

        return EmployeeProfile.MyEmployeeProfile.EMPLOYEES[self.__employee_id__] if self.__employee_id__ in EmployeeProfile.MyEmployeeProfile.EMPLOYEES else None

    @property
    def categories(self) -> dict[str, float]:
        """
        :return: All categories and their ratings for this assessment
        """

        return {a: b for a, b in self.__categories__.items()}
