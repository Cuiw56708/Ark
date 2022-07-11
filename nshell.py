import neutron as intrepreter
import sys

# try:
while True :
    print("\a")
    text = input("@neutron~$ ")
    if text == "quit":
        sys.exit(0)
    result, error = intrepreter.run("<shell.net>",text)
    
    if error :
        print(error)
    else:
        print(result)
# except Exception as e:
#     print("An unexpected error occured: ", e, sep="")
# except:
#     print()
