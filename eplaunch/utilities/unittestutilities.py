import inspect
import os


class UnitTestUtilities:

    def in_unit_test(self):
        current_stack = inspect.stack()
        for stack_frame in current_stack:
            for program_line in stack_frame[4]:  # This element of the stack frame contains
                if "unittest" in program_line:  # some contextual program lines
                    return True
        return False

    def tests_utilities_directory(self):
        utilities_path = os.path.dirname(__file__)
        eplaunch_path, tail = os.path.split(utilities_path)
        tests_path = os.path.join(eplaunch_path,"tests")
        tests_utilities_path = os.path.join(tests_path,"utilities")
        return tests_utilities_path