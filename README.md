# Local Funk

## What

Localfunk proxies lambda invocations to local code.

## Usage

- `pipenv install --dev localfunk`
- `pipenv run localfunk`

## Why

Serverless development leverages a lot of proprietry tools that are difficult to run locally. They can difficult to set up, and often lack features. For example `Sam local start-api`:

- requires `Sam build` to be run on every code change, which can be _very_ slow.
- doesn't currently support HTTP API
- doesn't currently support Custom Authorizers

There is a lot or effort put into trying to replicate API Gateway locally with `start-api` and it can be hard to keep features in sync with the deployed service.

Localfunk attempts to leverage Cloud services while still allowing local code changes to be run immediately, without a build or deploy step.

## How

- Ngrok is started locally
- Function code is packaged that proxies invocations to local code
- `Sam deploy` is run to deploy the template and the proxy function code
- A Flask server is started locally to route events to the local code
- The function CodeURI and environment variables are loaded to emulate the Lambda environment

Even though code is being run locally there will still need to be changes to the template  e.g changing permissions and since the localfunk build process is simpler than a full `Sam build`, it will be quicker to get these changes deployed.

The Lambda environment variables include a session token set from the function role, by loading the environment variables locally the local code will run using the role that is defined for the function.

## Possible Improvements

Run ngrok as a deamon and check for a running instance before starting a new one. Can also check template to see if ngrok has changed. This will speed up stopping and starting because there won't need to be a redeploy if it hasn't changed.

[Docker-lambda](https://github.com/lambci/docker-lambda) is currently not integrated but adding it would bring the local invocation closer to the real Lambda environment.

Localfunk currently only works with AWS::Serverless::Function and `Sam Deploy` but could work with raw Cloudformation.

This library only supports calling Python local Python code but the same pattern would work for other languages. Due to the way that the code is loaded and invocated it seems simpler to run Python code from Python but maybe it would work to create a generic CLI tool that could invoke any language.
