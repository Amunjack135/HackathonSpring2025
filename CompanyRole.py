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
                    MyCompanyRole.COMPANY_ROLES[index] = MyCompanyRole(KVP.KVP.decode(fstream.read()))

        MyCompanyRole.__LOADED__ = True
        return len(MyCompanyRole.COMPANY_ROLES)

    def __init__(self, kvp: KVP.KVP):
        """
        [Constructor] - Creates a new company role
        This will not add it to the internal listing and should not be called explicitly
        :param kvp: The company role's KVP information
        """

        self.__role_name__: str = kvp.CompanyRole.Name[0]
        self.__role__: str = kvp.CompanyRole.Role[0]
        self.__required_skills__: dict[str, float] = {skill: rank[0] for skill, rank in kvp.CompanyRole.RequiredSkills}
        self.__optional_skills__: dict[str, float] = {skill: rank[0] for skill, rank in kvp.CompanyRole.OptionalSkills}

    @staticmethod
    def get_uuids_from_role_name(role_name: str) -> tuple[int, ...]:
        """
        Gets all role uids for a given role name
        :param role_name: The role to check
        :return: The role uids matching this role
        """

        return tuple(uid for uid, role in MyCompanyRole.COMPANY_ROLES.items() if role.role.lower() == role_name.lower())

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
