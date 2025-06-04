from fastapi import APIRouter, File, UploadFile
from starlette.responses import FileResponse
from BackendApp.Logger import logger, LogLevel
import os

router = APIRouter()

@router.get(path="/file/download/", tags=["Files"])
async def download(path_to_file: str) -> FileResponse:
    try:
        return FileResponse(path_to_file)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /file/download/: {e}",
            module_name="API"
        )

@router.post(path="/file/upload_static/{dir:path}", tags=["Files"])
def upload(dir: str, file: UploadFile = File(...)) -> dict:
    try:
        contents = file.file.read()
        pwd = os.getcwd()
        new_filename = pwd + f"/BackendApp/static/{dir}/" + file.filename
        with open(new_filename, 'wb') as f:
            f.write(contents)
    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /file/upload_static/: {e}",
            module_name="API"
        )
        return {
            "status": "Failed",
            "message": f"There was an error uploading the file: {e}"
        }
    finally:
        file.file.close()

    return {
        "status": "Success",
        "message": new_filename
    }

@router.delete(path="/file/remove_static/{path_to_file:path}", tags=["Files"])
def remove(path_to_file: str):
    try:
        pwd = os.getcwd()
        filename = pwd + f"/BackendApp/static/{path_to_file}" 
        if (not os.path.exists(filename)):
            {
                "status": "Failed",
                "message": f"The file with the filename {filename} does not exist"
            }
        else:
            os.remove(path=filename)
            return {
                "status": "Success",
                "message": f"The file with the filename {filename} has been successfully deleted"
            }

    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /file/remove_static/: {e}",
            module_name="API"
        )
        return {
            "status": "Failed",
            "message": f"An error occurred while removing the file: {e}"
        }

@router.get(path="/file/get_static/{dir:path}", tags=["Files"])
def get_all(dir: str):
    try:
        pwd = os.getcwd()
        repo = pwd + f"/BackendApp/static/{dir}/"
        if (not os.path.exists(repo)):
            {
                "status": "Failed",
                "message": f"The repository with the directory name {dir} does not exist"
            }
        else:
            ls = []
            for file in os.listdir(repo):
                if (file != ".gitignore" and file != ".getkeep"):
                    joined_path = os.path.join(repo, file)
                    ls.append(joined_path)
            return {
                "status": "Success",
                "message": [path for path in ls]
            }

    except Exception as e:
        logger.log(
            level=LogLevel.ERROR,
            message=f"An error occurred in /file/get_static/: {e}",
            module_name="API"
        )
        return {
            "status": "Failed",
            "message": f"An error occurred while removing the file: {e}"
        }
