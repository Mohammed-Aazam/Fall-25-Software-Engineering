As a team, discuss and answer:

1. What is the engineering argument against the PM's request? (Focus on technical risk).

Technical debt will be introduced as cleaning up in a later cycle will increase the time to repair broken code since the tests haven't been run then and there and the context has been lost
Searching for the root caue for bugs will become difficult
The readability of the code which was maintained due to the linting will be reduced since the linting will have been skipped


2. What is the ethical responsibility you have to your future teammates (who will inherit this code)?

Our ethical responsibility to the people who will inherit the code will include multiple things such as:
Not increasing avoidable burden due to skipping tests
Keeping code readable and documenting changes that have been done and the why behind the same
Not transferring technical debt to people who haven't signed up for it


3. What is the ethical responsibility you have to your users? (Does "un-linted" or "un-tested" code have an ethical impact on them, or is it just an "internal problem"?)

Having untested code will cause errors and loss of time and money for the users, which we should avoid
Privacy may be harmed for the users due to skipping tests
The trust users have in us may break due to the consequences to our decision of skipping testing

4. The Decision: What is your team's official, professional response to the Product Manager?

We cannot approve for shipping the change un-linted and un-tested since it will create risks for both our users and technical teams.
This will eventually increase the total time cost due to the technical debt that will come as a consequence of this decision.
We can deliver this feature in a way that will minimize the delay in shipping while also keeping the critical tests and linting in place.
