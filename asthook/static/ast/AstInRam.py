
class AstInRam:

    projects = {}

    @classmethod
    def askpath(cls, project, path):
        if not project in cls.projects:
            return None
        if not path in cls.projects[project]:
            return None
        return cls.projects[project][path]

    @classmethod
    def addpath(cls, project, path, value):
        if not project in cls.projects:
            cls.projects[project] = {}
        cls.projects[project][path] = value

