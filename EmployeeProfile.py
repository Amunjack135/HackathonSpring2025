import CustomMethodsVI.Parser.KVP as KVP


class MyEmployeeProfile:
    def __init__(self, kvp: KVP.KVP):
        self.__employee_name__: str = kvp.EmployeeProfile.Name
        self.__skills__: list[str] = kvp.EmployeeProfile.Skills
        self.__project_ids__: list[int] = kvp.EmployeeProfile.ProjectIDs
        self.__performance_review_ids__: list[int] = kvp.EmployeeProfile.PerfReviewIDs
        self.__assessment_ids: list[int] = kvp.EmployeeProfile.AssessmentIDs
        self.__role__: str = kvp.EmployeeProfile.CurrentRole

