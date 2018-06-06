import inspect


class UnitTestUtilities:

    def in_unit_test(self):
        current_stack = inspect.stack()
        for stack_frame in current_stack:
            for program_line in stack_frame[4]:    # This element of the stack frame contains
                if "unittest" in program_line:       # some contextual program lines
                    return True
        return False