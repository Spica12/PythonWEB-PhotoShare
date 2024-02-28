# PythonWEB-PhotoShare


PythonWEB-PhotoShare is a REST API application constructed with the FastAPI framework. It allows customers to upload, organize, and transform photos, and have interaction with others thru feedback and ratings.

---

#Link to deploy


## Used Technologies 

| Technology  | Description                                      |
|--------------|--------------------------------------------------|
| FastAPI      | Modern Python framework for building APIs that allows for rapid development of high-performance APIs. |
| SQLAlchemy   | Python ORM (Object-Relational Mapping) that enables working with databases in an object-oriented style. |
| Passlib      | Library for securely storing and verifying passwords in Python.    |
| Qrcode       | Library for generating QR codes in Python.    |
| Alembic      | Database migration tool for SQLAlchemy, allowing for easy deployment of database schema changes. |
| PostgreSQL   | Object-relational database with high reliability and scalability, supporting SQL. |
| Cloudinary   | Service for managing images and videos, providing an API for uploading, storing, and optimizing media files. |
| Pydantic     | Library for data validation and serialization in Python, based on data type annotations. |
| Pillow       | Library for image processing and manipulation in Python.   |
| Psycopg2     | PostgreSQL database adapter for Python.    |
| PyJWT        | Library for working with JSON Web Tokens (JWT) in Python.   |


## Application functionality

### Authentication block

**Endpoints for user authentication:**
```
POST /api/auth/register
```
```
POST /api/auth/login
```
```
GET /api/auth/logout
```
```
GET /api/auth/refresh
``` 
```
GET /api/auth/confirmed_email/{token}
``` 
```
GET /api/auth/password-reset/{token}
``` 
```
POST /api/auth/password-reset
``` 


Users have three roles: admin, moderator, and user.

### Users block

**Endpoints for user management:**

- Retrieving the information of the currently authenticated user.
    ```
    GET /api/users/my_profile
    ```
- Editing email for currently authenticated user.
    ```
    PUT /api/users/my_profile/email
    ```
- Change avatar for current user.
    ``
    PUT /api/users/my_profile/avatar
    ````
- See another user's profile.
    ```
    GET /api/users/{username}
    ```
- The ability for the administrator to change the role of any user, confirm his registration or cancel it and ban him.
    ```
    PUT /api/users/{username}
    ```

### Photos block

**Endpoints for photo management:**

- Show all photos for all users, including for those not registered.
    ```
    GET /api/photos/
    ```
- Upload photo with description and tags.
    ```
    POST /api/photos/
    ```
- Show photo by id with comments if it is.
    ```
    GET /api/photos/{photo_id}
    ```
- Adding comment to the photo by id only for registered users.
    ```
    POST /api/photos/{photo_id}
    ```
- Delete photos.
    ```
    DELETE /api/photos/{photo_id}
    ```
- Changing photo description.
    ```
    PUT /api/photos/{photo_id}
    ```
- Settin rate to the photo.
    ```
    POST /api/photos/{photo_id}/set-rate
    ```
- Get url or show photo by url from qrcode (generated in post method) for transformation with object id for photo with photo id.
    ```
    GET /api/photos/{photo_id}/transform
    ```
- Crate photo transformation for current photo or Generate qr code for photo transformation.
    ```
    POST /api/photos/{photo_id}/transform
    ```
- Show all rates for current image. Only for admin and moderators. To see what rate and who was set it.
    ```
    GET /api/photos/{photo_id}/rating
    ```  
- Deleting rate for photo by photo id and username. Only for admins and moderators.
    ```
    DELETE /api/photos/{photo_id}/rating/{username}
    ``` 
- Generate links to photos and transformed photos for viewing as URL and QR-code    
- Available basic photo transformations using Cloudinary services.
- All registered users can upload photos with descriptions and tags.
- Administrators and moderators can delete photos and comments.
- All registered users can rate photos, but only administrators and moderators can delete ratings.
- All registered users can leave comments on photos.



## Installation

Before installing pygame, you must check that Python is installed on your machine. To find out, open a command prompt (if you have Windows) or a terminal (if you have MacOS or Linux) and type this:
```Shell
  pip --version
```
If a message such as "Python 3.12.2" appears, it means that Python is correctly installed. If an error message appears, it means that it is not installed yet. You must then go to the official [website](https://www.python.org/) and follow the instructions.

Once Python is installed, you have to perform a final check: you have to see if pip is installed. Generally, pip is pre-installed with Python but we are never sure. Same as for Python, type the following command:
```Shell
  pip --version
```
If a message such as "pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)" appears, you are ready to install PythonWEB-PhotoShare.

Activate your virtual environment and follow the instructions below:
for Windows:
```Shell
  python -m venv venv
  venv\Scripts\activate
```
for MacOS and Linux:
```Shell
  python3 -m venv venv
  source venv/bin/activate
```
Or with poetry:
```Shell
  poetry install
  poetry shell
```

- Clone this link to repository to your terminal in IDE.
```Shell
  https://github.com/Spica12/PythonWEB-PhotoShare.git
```

- Install dependencies.
```Shell
  pip install -r requirements.txt
```
*or with poetry*
```Shell
  poetry install
```

- Setup the ".env" file.
```Shell
  cp .env.example .env
```
*and fill all needed information*

- Run the application.
```Shell
  uvicorn main:app --reload
```



### More information about us:

## Authors

- [Spica12](https://github.com/Spica12)
- [Artificer-ua](https://github.com/Artificer-ua)
- [SergiyDovgopolyk](https://github.com/SergiyDovgopolyk)
- [Andriiok](https://github.com/Andriiok)
- [Bodya3836](https://github.com/Bodya3836)

## License

[MIT License](https://github.com/Spica12/PythonWEB-PhotoShare/blob/main/LICENSE).
