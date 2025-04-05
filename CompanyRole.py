from __future__ import annotations

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem


class MyCompanyRole:
    COMPANY_ROLES: dict[int, MyCompanyRole] = {}

    @staticmethod
    def load(root_dir: str) -> int:
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

        return len(MyCompanyRole.COMPANY_ROLES)

    def __init__(self, kvp: KVP.KVP):
        self.__role_name__: str = kvp.CompanyRole.Name[0]
        self.__role__: str = kvp.CompanyRole.Role[0]
        self.__required_skills__: dict[str, float] = {skill: rank[0] for skill, rank in kvp.CompanyRole.RequiredSkills}
        self.__optional_skills__: dict[str, float] = {skill: rank[0] for skill, rank in kvp.CompanyRole.OptionalSkills}

    @property
    def role_name(self) -> str:
        return self.__role_name__

    @role_name.setter
    def role_name(self, name: str):
        assert isinstance(name, str) and len(name) >= 2, 'Invalid role name'
        self.__role_name__ = name

    @property
    def role(self) -> str:
        return self.__role__

    @role.setter
    def role(self, name: str):
        assert isinstance(name, str) and len(name) >= 2 and all(x.isalnum() for x in name), 'Invalid role literal ID'
        self.__role__ = name

    @property
    def required_skills(self) -> dict[str, float]:
        return {a: b for a, b in self.__required_skills__}

    @property
    def optional_skills(self) -> dict[str, float]:
        return {a: b for a, b in self.__optional_skills__}
