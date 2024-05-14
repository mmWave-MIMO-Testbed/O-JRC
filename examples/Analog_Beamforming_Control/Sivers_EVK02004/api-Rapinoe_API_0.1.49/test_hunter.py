import sys
import hunter

with open('hunter_output.log','a') as f:

    hunter.trace(module='posixpath', action=hunter.CallPrinter(stream=f))

    def example_function():
            for x in range (10):
                print(f"x is {x}")

    example_function()

