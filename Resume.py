from __future__ import annotations

import math
import zlib

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem


class MyResume:
    RESUMES: dict[slice, dict[int, MyResume]] = {}
    BATCH_FILES: dict[slice, FileSystem.File] = {}

    @staticmethod
    def load(root_dir: str) -> int:
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
                    batchdex: list[str] = file.filename().split('_')
                    batch: slice = slice(int(batchdex[1]), int(batchdex[2]))
                    resumes: KVP.KVP = KVP.KVP.decode(fstream.read())
                    batch_listing: dict[int, MyResume] = {}
                    fname: str = file.filepath()[len(root_dir.dirpath()):]

                    for index, resume in resumes:
                        batch_listing[int(index)] = MyResume(zlib.decompress(resume[0]).decode() if len(resume) > 0 else '')

                    MyResume.RESUMES[batch] = batch_listing
                    MyResume.BATCH_FILES[batch] = FileSystem.File(fname)

        return len(MyResume.RESUMES)

    @staticmethod
    def save(root_dir: str) -> None:
        root_dir: FileSystem.Directory = FileSystem.Directory(root_dir)

        if not root_dir.exists():
            root_dir.create()

        for batch, resumes in MyResume.RESUMES.items():
            batch_file: FileSystem.File = MyResume.BATCH_FILES[batch]
            parent: FileSystem.Directory = batch_file.parentdir()
            batch_file = root_dir.cd(parent.dirpath()).file(batch_file.basename())

            if not parent.exists():
                parent.create()

            compiled_resumes: dict[int, bytes] = {}
            keys: tuple[int, ...] = tuple(sorted(resumes.keys()))

            for index in keys:
                resume: MyResume = resumes[index]
                compiled_resumes[index] = zlib.compress(resume.contents.encode(), zlib.Z_BEST_COMPRESSION)

            highest_digit: int = math.ceil(math.log10(max(batch.start, batch.stop)))
            kvp_compiled: KVP.KVP = KVP.KVP(None, {str(index).zfill(highest_digit): [encoded] for index, encoded in compiled_resumes.items()})

            with batch_file.open('w') as fstream:
                fstream.write(kvp_compiled.encode(True))

    @staticmethod
    def get_resume(batch: slice, index: int) -> MyResume | None:
        return MyResume.RESUMES[batch][index] if batch in MyResume.RESUMES and index in MyResume.RESUMES[batch] else None

    def __init__(self, resume: str):
        self.__resume__: resume = str(resume)

    @property
    def contents(self) -> str:
        return self.__resume__
