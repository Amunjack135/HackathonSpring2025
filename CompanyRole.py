from __future__ import annotations

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem


class MyCompanyRole:
    """
    Basic class holding company role information
    """

    COMPANY_ROLES: dict[int, MyCompanyRole] = {}
    __LOADED__: bool = False

    @staticmethod
    def load(root_dir: str) -> int:
        """
        Loads all company roles in the specified directory
        :param root_dir: The directory to load from
        :return: The number of loaded company roles
        """

        if MyCompanyRole.__LOADED__:
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
                    MyCompanyRole.COMPANY_ROLES[index] = MyCompanyRole(offset, KVP.KVP.decode(fstream.read()))

        MyCompanyRole.__LOADED__ = True
        return len(MyCompanyRole.COMPANY_ROLES)

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

        for uid, role in MyCompanyRole.COMPANY_ROLES.items():
            role_file: FileSystem.File = root_dir.file(role.__file_offset__)
            parent: FileSystem.Directory = role_file.parentdir()

            if not parent.exists():
                parent.create()

            with role_file.open('w') as fstream:
                fstream.write(role.to_kvp().encode(True))

    @staticmethod
    def get_uuids_from_role_name(role_name: str) -> tuple[int, ...]:
        """
        Gets all role uids for a given role name
        :param role_name: The role to check
        :return: The role uids matching this role
        """

        return tuple(uid for uid, role in MyCompanyRole.COMPANY_ROLES.items() if role.role.lower() == role_name.lower())

    def __init__(self, file_offset: str, kvp: KVP.KVP):
        """
        [Constructor] - Creates a new company role
        This will not add it to the internal listing and should not be called explicitly
        :param file_offset: The relative path of this file relative to the root directory
        :param kvp: The company role's KVP information
        """

        self.__file_offset__: str = str(file_offset)
        self.__role_name__: str = str(kvp.CompanyRole.Name[0])
        self.__role__: str = str(kvp.CompanyRole.Role[0])
        self.__active__: bool = bool(kvp.CompanyRole.IsActive[0])
        self.__required_skills__: dict[str, float] = {str(skill): float(rank[0]) for skill, rank in kvp.CompanyRole.RequiredSkills}
        self.__optional_skills__: dict[str, float] = {str(skill): float(rank[0]) for skill, rank in kvp.CompanyRole.OptionalSkills}

    def to_kvp(self) -> KVP.KVP:
        """
        Converts this object to KVP for saving
        :return: A KVP object
        """

        mapping: dict = {
            'CompanyRole': {
                'Name': [self.__role_name__],
                'Role': [self.__role__],
                'IsActive': [self.__active__],
                'RequiredSkills': {skill: [rank] for skill, rank in self.__required_skills__.items()},
                'OptionalSkills': {skill: [rank] for skill, rank in self.__optional_skills__.items()}
            }
        }
        return KVP.KVP(None, mapping)

    @property
    def role_name(self) -> str:
        """
        Gets this role's friendly name
        :return: This role's friendly name
        """

        return self.__role_name__

    @role_name.setter
    def role_name(self, name: str):
        """
        Sets this role's friendly name
        :param name: The new name, must be a string at least 2 characters long
        :return: NONE
        """

        assert isinstance(name, str) and len(name) >= 2, 'Invalid role name'
        self.__role_name__ = name

    @property
    def role(self) -> str:
        """
        Gets this role's name
        :return: This role's name
        """

        return self.__role__

    @role.setter
    def role(self, name: str):
        """
        Sets this role's name
        :param name: The new name, must be a string at least 2 characters long containing only alphanumeric characters
        :return: NONE
        """

        assert isinstance(name, str) and len(name) >= 2 and all(x.isalnum() for x in name), 'Invalid role literal ID'
        self.__role__ = name

    @property
    def active(self) -> bool:
        """
        Gets whether this role is active
        :return: This role's activeness
        """

        return self.__active__

    @active.setter
    def active(self, activeness: str):
        """
        Sets this role's activeness
        :param activeness: The new name, must be a bool
        :return: NONE
        """

        assert isinstance(activeness, bool), 'Invalid role activeness'
        self.__active__ = activeness

    @property
    def required_skills(self) -> dict[str, float]:
        """
        Gets this employee's name
        :return: This employee's name
        """

        return {a: b for a, b in self.__required_skills__.items()}

    @property
    def optional_skills(self) -> dict[str, float]:
        """
        Gets this employee's name
        :return: This employee's name
        """

        return {a: b for a, b in self.__optional_skills__.items()}
