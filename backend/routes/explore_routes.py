from uuid import UUID

from auth.auth_bearer import AuthBearer, get_current_user
from fastapi import APIRouter, Depends, Query
from models.brains import Brain
from models.settings import common_dependencies
from models.users import User

explore_router = APIRouter()


@explore_router.get("/explore", dependencies=[Depends(AuthBearer())], tags=["Explore"])
async def explore_endpoint(brain_id: UUID = Query(..., description="The ID of the brain"),current_user: User = Depends(get_current_user)):
    """
    Retrieve and explore unique user data vectors.
    """
    brain = Brain(id=brain_id)
    unique_data = brain.get_unique_brain_files()

    unique_data.sort(key=lambda x: int(x["size"]), reverse=True)
    return {"documents": unique_data}


@explore_router.delete(
    "/explore/{file_name}", dependencies=[Depends(AuthBearer())], tags=["Explore"]
)
async def delete_endpoint(file_name: str, current_user: User = Depends(get_current_user), brain_id: UUID = Query(..., description="The ID of the brain")):
    """
    Delete a specific user file by file name.
    """
    brain = Brain(id=brain_id)
    brain.delete_file_from_brain(file_name)

    return {"message": f"{file_name} of brain {brain_id} has been deleted by user {current_user.email}."}


@explore_router.get(
    "/explore/{file_name}", dependencies=[Depends(AuthBearer())], tags=["Explore"]
)
async def download_endpoint(
    file_name: str, current_user: User = Depends(get_current_user)
):
    """
    Download a specific user file by file name.
    """
    # check if user has the right to get the file: add brain_id to the query 

    commons = common_dependencies()
    response = (
        commons["supabase"]
        .table("vectors")
        .select(
            "metadata->>file_name, metadata->>file_size, metadata->>file_extension, metadata->>file_url",
            "content",
        )
        .match({"metadata->>file_name": file_name})
        .execute()
    )
    documents = response.data
    return {"documents": documents}
