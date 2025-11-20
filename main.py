import subprocess
import easygui


def run_script(script_path):
    result = subprocess.run(["python", script_path],
                   check=True,
                   capture_output=True,
                   text=True)
    print(result.stdout)

def main():
    choice = easygui.buttonbox("Select two PDFs for comparison:", choices=["Upload Left PDF", "Upload Right PDF"])

    if choice == "Upload Left PDF":
        choices = ["Left PDF Already Uploaded", "Upload Right PDF"]
    else:
        choices = ["Upload Left PDF", "Right PDF Already Uploaded"]
    run_script("stellantisPDF.py")

    choice = easygui.buttonbox("Select two PDFs for comparison:", choices=choices)
    run_script("stellantisPDF.py")
    
    run_script("compareExtractedPDF.py")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()