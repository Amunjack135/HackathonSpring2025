from __future__ import annotations

import numpy
import typing
import pickle

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem


class MyEmployeeProfile:
    EMPLOYEES: dict[int, MyEmployeeProfile] = {}

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
                    MyEmployeeProfile.EMPLOYEES[index] = MyEmployeeProfile(KVP.KVP.decode(fstream.read()))

        return len(MyEmployeeProfile.EMPLOYEES)

    def __init__(self, kvp: KVP.KVP):
        self.__employee_name__: str = kvp.EmployeeProfile.Name[0]
        self.__skills__: list[str] = kvp.EmployeeProfile.Skills
        self.__project_ids__: list[int] = [int(x) for x in kvp.EmployeeProfile.ProjectIDs]
        self.__performance_review_ids__: list[int] = [int(x) for x in kvp.EmployeeProfile.PerfReviewIDs]
        self.__assessment_ids: list[int] = [int(x) for x in kvp.EmployeeProfile.AssessmentIDs]
        self.__roles__: list[str] = kvp.EmployeeProfile.CurrentRole
        self.__resume_id__: int = -1 if len(kvp.EmployeeProfile.ResumeID) == 0 else int(kvp.EmployeeProfile.ResumeID[0])
        self.__image__: numpy.ndarray = numpy.full((512, 512, 4), 0, numpy.uint8) if len(kvp.EmployeeProfile.Image) == 0 else numpy.frombuffer(kvp.EmployeeProfile.Image[0], dtype=numpy.uint8)
        self.__extra_meta__: typing.Any = None if len(kvp.EmployeeProfile.Extra) == 0 else pickle.loads(kvp.EmployeeProfile.Extra[0])
        self.__bio__: str = '' if len(kvp.EmployeeProfile.Bio) == 0 else kvp.EmployeeProfile.Bio[0]
