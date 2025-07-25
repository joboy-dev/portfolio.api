import sys
import pathlib
from slugify import slugify
from sqlalchemy.orm import Session

ROOT_DIR = pathlib.Path(__file__).parent.parent.parent

# ADD PROJECT ROOT TO IMPORT SEARCH SCOPE
sys.path.append(str(ROOT_DIR))

from api.db.database import get_db_with_ctx_manager
from api.v1.models.profile import Profile


with get_db_with_ctx_manager() as db:  
    _, _, count = Profile.fetch_by_field(db, paginate=False)
    if count > 0:
        print("Profile already exists")
        exit()
    
    profile = Profile.create(
        db=db,
        first_name='Oluwakorede',
        last_name='Adegbehingbe',
        email="oluwakoredeadegbehingbe@gmail.com",
        image_url="https://ui-avatars.com/api/?name=Oluwakorede+Adegbehingbe",
        title="Software Engineer"
    )
    
    print(profile.to_dict())