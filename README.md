# AutomatedCurtains

## Frontend
The 'frontend' is comprised of a few different components. First there is the basic HTML form to get the data from the user.
Using javascript we made the form send the data in json to an API. We used FastAPI to make a simple api which parses the curtain
setting passed to it to generate a message that is sent to the pi through AWS IoT MQTT.
We are using a basic docker container to mimic a server that acts as the 'middleware' between the website and the AWS server. The 
container just hosts the api. We went this route for a couple reasons. First, we were having trouble getting the AWS sdk working in
javascript and found it much easier to do in Python. Second, if this were a real product we were shipping to real users we would want
to keep the components seperate for security and ease of use reasons. ie We wouldn't want our users to have to store the AWS certifications
and keys on their own computers.