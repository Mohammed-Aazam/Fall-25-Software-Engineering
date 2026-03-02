#### ICE 17: "The API Blueprint"
* **Date:** 2025-12-18
* **Roles:**
    * Repo Admin: `@skarana`
    * Process Lead (Ops): `@adhgaidh`
    * Dev Crew (Backend): `@mtadipat`
    * QA Crew: `@jostorr`
* **Summary:** Flask’s jsonify can only serialize basic Python data types like dictionaries, lists, strings, and numbers. Joke objects are custom Python objects (or ORM models) and are not JSON-serializable by default. We therefore have to manually loop through each Joke object and convert it into a dictionary containing only JSON-safe fields before returning it in the response.
* **Evidence:**
    ![alt text](<jsonify_icex17-image.png>)

#### HW 11 (A16): Persisting the AI Analysis
* **Date:** 2025-12-18
* **Chosen PR:** [[Link](https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/71)]
* **Justification:** This implementation was chosen to follow standard Flask-Migrate and container best practices by keeping schema changes explicit and controlled. Migrations are generated separately from deployment so database changes are predictable, reviewable, and reproducible across environments.
* **Reflection:** flask db migrate does not change the database. It only compares the current models to the existing schema and generates a migration script.
flask db upgrade actually applies those migration scripts and updates the production database (the Postgres container). Therefore, flask db upgrade is the command that changes the production database.

#### HW 10 (A15): The Deployment Spec
* **Date:** 2025-12-18
* **Chosen PR:** [[Link](https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/69)]
* **Justification:** his implementation was chosen because it cleanly separates image build from runtime behavior, making the deployment more reliable across different environments. Using a startup script allows configuration and dependencies to be resolved before the application runs.
* **Reflection:** We could not use RUN flask db upgrade in the Dockerfile because Docker build steps run at image build time, when the database may not be available and environment variables may not be set. Running migrations in boot.sh ensures they execute at container startup, when the database connection is ready and matches the deployment environment.

#### ICE 16: "The AI Rater"
* **Date:** 2025-12-17
* **Roles:**
    * Repo Admin: `@skarana`
    * Process Lead (Ops): `@adhgaidh`
    * Dev Crew (Backend): `@mtadipat`
    * QA Crew: `@jostorr`
* **Summary:** Added the 'ai-service' container to our stack. Updated routes.py to send new jokes to the AI service via HTTP POST. Successfully verified that the AI returns a rating flash message.
* **Evidence:**
    ![alt text](ai_evidence.png)


#### HW 7: Pragmatic Engineering (A 12-Factor App Analysis)
* **Date:** 2025-12-16
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Link to Final Report:** https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/blob/hw7-12factor-report/REPORT.md
* **Assigned Rules:**
    * `@skarana`: Rule [V - Build, Release, Run]
    * `@mtadipat`: Rule [III - Config]
    * `@jostorr`: Rule [VII - Port Binding]
    * `@adhgaidh`: Rule [I - Codebase]
* **Summary of Work:** We got to learn the ways we as engineers can break rules when needed, when the benefits far outweigh the trade-offs. We also got to see the different situations that we might be in while building an applications and how to think about it, considering all the situations.


#### ICE 15: "Shipping Containers"
* **Date:** 2025-12-11
* **Roles:**
    * Repo Admin: `@adhgaidh`
    * Dev Crew (Systems): `@skarana`
    * Process Lead (Ops): `@mtadipat`
    * QA Crew: `@jostorr`
* **Summary:** 
We made a Dockerfile and docker-compose.yml and migrated from SQLite to PostgreSQL
* **Reflection:** Discussion point for the log: “Why did we have to use --host=0.0.0.0 in the Dockerfile? What happens if we change the POSTGRES_PASSWORD in the compose file but not the web environment variables?”
The host 0.0.0.0 lets the app accept requests from inside its own container.
If we change the password only in the compose file, the database connetion will break because the credentials will no longer match.


#### ICE 14: "Paying Our Debt" (Security Refactor & Testing)
* **Date:** 2025-12-10
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@adhgaidh`
    * Process Lead: `@skarana`
    * QA Crew: `@mtadipat`, `@jostorr`
* **Summary of Work:** We added the secret_key to the .env file and added a new security test
* **Evidence & Reflection:** We just proved our app is "secure by default" against XSS. Why is it still important to write this test? What does the test protect us from in the future?
We should be able kep checking in case any code changes or developer mistakes introduce the XSS.


#### HW 9 (A14): The Full-Stack Logger
* **Date:** 2025-12-10
* **Chosen PR:** https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/61
* **Justification:** Has the cleanest code, with all tests running fine.
* **Individual Contributions:**
    * **`@skarana`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/61
    * **`@mtadipat`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/59
    * **`@jostorr`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/62
    * **`@adhgaidh`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/60
* **Reflection:** The model UserAction was implemented to other places other than the one done in the ICE, and the code was easily added.  

#### ICE 13: "The Logging Service"
* **Date:** 2025-12-10
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@adhgaidh`
    * Dev Crew (Backend): `@jostorr`
    * Process Lead: `@skarana`
    * QA Crew: `@mtadipat`
* **Summary of Work:** Paid off our technical debt by creating a new 'UserAction' model with class constants. We refactored the 'admin_edit_joke' route to 'connect the wire' and save the justification to this table. The admin panel is now a full audit log viewer, and our tests confirm the log is created.
* **Evidence & Reflection:** We just built a `UserAction` table that logs what users do and when. As engineers, what are the **ethical** or **operational** questions we should be asking? For example, who "owns" this data? What happens when this table has a billion rows? Can a user request their history be deleted (e.g., "the right to be forgotten")?
We should ask who has access to the logs, and ensure that the logging aligns with the privacy and ethical expectations. We also need to plan for operational issues as the table grows.


#### HW 7 (A13): The "@admin_required" Decorator
* **Date:** 2025-12-09
* **Chosen PR:** https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/53
* **Justification:** Passes tests and has the bonus credit implementation
* **Individual Contributions:**
    * **`@jostorr`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/56
    * **`@mtadipat`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/55
    * **`@skarana`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/54
    * **`@adhgaidh`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/53
* **Reflection:** Decorators make it easier to be able to switch code up in case there is a dfesign change, rathr having to change things everywhere a change needs to be implemented.


### Assignment 12 (A12): Admin Modify User
* **Date:** 2025-12-08
* **Chosen PR:** https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/42
* **Justification:** The PR was up to mark with the extra credit, and has clean code.
    * **`@skarana`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/44
    * **`@jostorr`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/46
    * **`@mtadipat`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/45
    * **`@adhgaidh`**: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/42
* **Reflection:** The most difficult part here was making sure the two forms interact well in the "Delete Joke" functionality. This excercise was good to understand implementing previously seen similar code.


#### ICE 12: "Joke Ratings" (Many-to-Many)
* **Date:** 2025-12-04
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@adhgaidh`
    * Process Lead: `@skarana`
    * Dev Crew (Backend): `@mtadipat`
    * QA Crew: `@jostorr`
* **Summary of Work:** Implemented the Joke Rating feature, which includes creating the model and building a form for the same
* **Evidence & Reflection:** This was our first many-to-many relationship. What other features could we build using this *exact* database pattern (a "join" table with a "payload")?
We can have transactions linked to a user in a shopping store(for example Aldi, Target) that would be similar to the database pattern.


#### ICE 11: "Admin Powers & Inheritance"
* **Date:** 2025-12-04
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`

* **Roles:**
    * Repo Admin: `@adhgaidh`
    * Dev Crew (Backend): `@jostorr`
    * Process Lead: `@skarana`
    * QA Crew: `@mtadipat`
* **Summary of Work:** We refactored the app to have .env files, and added admin specific commands for edit joke
* **Evidence & Reflection:** This was our first time using inheritance. How might extending `JokeForm` and `edit_joke.html` impact our ability to maintain this code base overtime? We added the `justification` field at this point in the project to demonstrate that a decoupled front-end and back-end allows greater flexability. However, what are the trade-offs of this approach?
Changes to the parent forms will affect the child forms
May become difficult to manage shared forms and logic increases for extra roles if added(like moderator etc.)


#### HW 5: Edit and Delete Jokes (Team Best)
* **Date:** 2025-12-04
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`

* **Individual PRs (Required for individual credit):**
    * `@skarana`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/26
    * `@mtadipat`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/31
    * `@jostorr`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/24
    * `@adhgaidh`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/32

* **"Team Best" Selection:**
    * **Chosen PR:** https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/26
    * **Justification:** The tests included everything needed and had the challenge implemented into it as well
    

#### ICE 10: The "Profile Page" (A Filtered Read)
* **Date:** 2025-XX-XX
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@mtadipat`
    * Process Lead: `@jostorr`
    * Dev Crew: `@skarana`, `@adhgaidh`
* **Summary of Work:** Created and tested a new dynamic route `/profile/<username>`, built and tested the `profile.html` template to render a user's jokes, and updated and tested the navigation and index page to link to it.
* **Evidence & Reflection:** Look at the `profile` route. What does the `.first_or_404()` method do? Why is this a better choice than `.first()`?
* When there is an error in the web interface side, `first_or_404()` is better equipped to handle the error on the database side than just `first()` by setting a `NotFound` flag on queries that do not have any inputs.


#### HW 4: Change Password Feature (Team Best)
* **Date:** 2025-11-17
* **Team Members Present:** `@github-user1`, `@github-user2`, ...

* **Individual PRs (Required for individual credit):**
    * `@mtadipat`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/23
    * `@jostorr`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/20
    * `@skarana`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/25
    * `@adhgaidh`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/22

* **"Team Best" Selection:**
    * **Chosen PR:** https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/22
    * **Justification:** This pull request has been chosen as the best since it has clean code, implemented all the requirements and done the challenge.


#### ICE 9: The "Front Door" (User Registration & Login)
* **Date:** 2025-11-05
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@mtadipat`
    * Process Lead: `@jostorr`
    * Dev Crew: `@skarana`, `@adhgaidh`
* **Summary of Work:** "Installed flask-wtf, defined the `LoginForm` and `RegistrationForm` in `forms.py`, and implemented the `login` and `register` routes in `routes.py` to handle form validation and user creation."
* **Evidence & Reflection:** What is the purpose of `form.validate_on_submit()`? What two things does it check for before returning `True`?
* It checks if the entered details belong to the authorized user or not
* Also if the user is registered or not.


#### ICE 8: Enforcing Quality (The Refactoring Workshop)
* **Date:** 2025-10-29
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@skarana`
    * Process Lead: `@adhgaidh`
    * Dev Crew: `@mtadipat`, `@jostorr`
* **Summary of Work:** : Refactored the app from app.py to the moj/ package, fixed all imports, wrote the first pytest for the '/' route, and added a flake8 linting job to main.yml.
* **Evidence & Reflection:** Discuss as a team: which new automated check (`pytest` or `flake8`) do you think will provide more *immediate value* to your team's workflow, and why?
flake8 will provide more imediate value to our workflow as we have a lot of code that is not up to mark with pep8. The pytest will be be of great use in the longer run.


#### ICE 7: The Ministry's Filing Cabinet
* **Date:** 2025-XX-XX
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
    * Repo Admin: `@skarana`
    * Process Lead: `@adhgaidh`
    * Dev Crew: `@mtadipat`, `@jostorr`
* **Summary of Work:** Installed and configured Flask-SQLAlchemy and Flask-Migrate for SQLite, defined User and Joke models, and ran the initial database migration to create the corresponding tables.
* **Evidence & Reflection:** In the migration script, the upgrade() function applies new database changes (like creating or altering tables), while the downgrade() function reverses those changes, allowing you to roll back to the previous database state.


#### ICE 2: The CI/CR "Fire Drill"
* **Date:** 2025-10-23
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
* Repo Admin: `@skarana`
* Process Lead: `@adhgaidh`
* Dev Crew: `@mtadipat`, `@jostorr`
* **Summary of In-Class Work:** We successfully validated our team's CI/CR
process.
1. `Dev Crew` pushed `main.yml` and got a **Green Check ✅ **.
2. `Dev Crew` pushed a failing test, getting a **Red X ❌ **.
3. `Process Lead` opened a PR and assigned all members.
4. The entire team commented, and the `Repo Admin` formally
**"Requested Changes"  **.
5. `Dev Crew` pushed the fix, getting a new **Green Check ✅ **.
6. `Repo Admin` **"Approved" 👍 ** the PR.
* **Evidence & Reflection:** We just proved our *team's process* works.
How does this in-class "validation sprint" help de-risk the *individual*
homework, where every member has to do this loop themselves?
This validation sprint firstly helps with all the team members understanding
how the whole process flows without having all the pressure on themselves.
It also helps with the automatic testing with the runners that have been set up
on each member's machine, since having it pre-setup will make the individual assignment
less stressful. 
* **Homework Evidence Links (To be filled out by 11:59 PM):**
* `@adhgaidh`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/5
* `@skarana`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/6
* `@mtadipat`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/7
* `@jostorr`: https://github.iu.edu/FA25-SE1-Team13/FA25-SE1-Team13-moj/pull/8


#### ICE 1: MoJ Kickoff - Repo & Round-Trip Sync
* **Date:** 2025-10-22
* **Team Members Present:** `@skarana`, `@mtadipat`, `@jostorr`, `@adhgaidh`
* **Roles:**
* Repo Admin: `@skarana`
* Process Lead: `@adhgaidh`
* Dev Crew: `@mtadipat`, `@jostorr`
* **Summary of Work:** Created the repo. The Process Lead pushed the test
scaffold (Sync 1). The Dev Crew locally verified `pytest` and `flask run`
*before* pushing the `app.py` file. Completed a final round-trip sync
(Sync 2).
* **Evidence & Reflection:** In Part 5, the `Dev Crew` manually ran pytest
to get local evidence. This process relies on trust. What is the
professional risk of a workflow that relies on trusting every engineer to
remember to run tests, and how does this build the case for automation
(CI)?
Automation will solve the issues of human error, missed bugs and inconsistency by consistent testing every time our code changes. 
