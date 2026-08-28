# Deploying GreenHealth on Vercel

## Recommended method

1. Extract this ZIP and push its contents to a new GitHub repository. The files
   must be at the repository root (for example, `manage.py` and `vercel.json`
   must not be inside an extra `fixed_project` folder).
2. In Vercel, choose **Add New > Project**, import that repository, and leave
   the framework preset as **Other**.
3. Keep the root directory as `./` and deploy. Do not set custom build or output
   commands.
4. Add these environment variables in **Project Settings > Environment
   Variables** and redeploy:

   - `SECRET_KEY`: a long random value
   - `DEBUG`: `False`
   - `DEMO_MODE`: `True`

## Database and uploaded images

The included SQLite database is copied to Vercel's temporary `/tmp` directory.
It is suitable for this demo, but changes can disappear after a serverless
restart. For persistent accounts, diagnoses, and uploads, configure a hosted
PostgreSQL `DATABASE_URL` and Cloudinary variables:

- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Redeploying the existing Vercel project

Replace the repository files with this clean project, commit and push, then use
**Deployments > Redeploy** in Vercel. If Vercel keeps an old build, redeploy
once with **Use existing Build Cache** disabled.
