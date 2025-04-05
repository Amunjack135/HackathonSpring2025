import cv2
import datetime
import numpy
import PIL.Image
import tkinter.filedialog as fd
import zlib

import CustomMethodsVI.Parser.KVP as KVP
import CustomMethodsVI.FileSystem as FileSystem


def main():
    name: str = input('Employee Name: ')
    skills: tuple[str, ...] = tuple(skill.strip().lower() for skill in input('Employee Skills: (comma separated) ').split(',') if len(skill) > 0)
    projects: tuple[int, ...] = tuple(int(project) for project in input('Employee Project IDs: (comma separated) ').split(',') if len(project) > 0)
    perf_reviews: tuple[int, ...] = tuple(int(review) for review in input('Employee Review IDs: (comma separated) ').split(',') if len(review) > 0)
    assessments: tuple[int, ...] = tuple(int(assessment) for assessment in input('Employee Assessment IDs: (comma separated) ').split(',') if len(assessment) > 0)
    roles: tuple[str, ...] = tuple(role.strip().lower() for role in input('Employee Roles: (comma separated) ').split(',') if len(role) > 0)
    resume: str = input('Employee Resume ID: (int,int,int) ')
    resume_index: tuple[int, ...] = tuple() if len(resume) == 0 else tuple(int(rid) for rid in resume.split(','))
    start_date: datetime.datetime = datetime.datetime.strptime(input('Start Date: (DD/MM/YYYY-HH:MM:SS)'), '%d/%m/%Y-%H:%M:%S').astimezone(datetime.timezone.utc)
    bio: str = input('Employee Bio: ')
    image_file: str = fd.askopenfilename(defaultextension='png', filetypes=(('Images', ('.png', '.jpg', '.jpeg')),))

    if image_file is None:
        return

    pillow: PIL.Image.Image = PIL.Image.open(image_file).convert('RGBA')
    image: numpy.ndarray = numpy.array(pillow)
    image = cv2.resize(image, (512, 512))

    mapping: dict = {
        'EmployeeProfile': {
            'Name': [name],
            'Skills': skills,
            'ProjectIDs': projects,
            'PerfReviewIDs': perf_reviews,
            'AssessmentIDs': assessments,
            'CurrentRole': roles,
            'ResumeID': resume_index[:3],
            'StartDate': start_date.timestamp(),
            'Image': [zlib.compress(image.tobytes(), zlib.Z_BEST_COMPRESSION)],
            'Extra': [],
            'Bio': [zlib.compress(bio.encode())],
            'DigitalPortfolio': {}
        }
    }

    fname: str = fd.asksaveasfilename(defaultextension='.kvp', filetypes=(('Key Value Pair Files', ('.kvp',)),))

    if fname is None or len(fname) == 0:
        return

    file: FileSystem.File = FileSystem.File(fname)

    with file.open('w') as f:
        f.write(KVP.KVP(None, mapping).encode(True))


if __name__ == '__main__':
    main()