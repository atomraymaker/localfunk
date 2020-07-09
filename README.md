# Local Funk

## What

Localfunk proxies lambda invocations to local code.

## Usage

- `pipenv install --dev localfunk`
- Run `localfunk` in the Sam project folder

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

The current code build process builds code into .aws-sam/build similar to how `Sam build` does. For this to work it is necesary to alter the CodeUri in the template. It may speed things up to alter the template to include the code inline instead.

[Docker-lambda](https://github.com/lambci/docker-lambda) is currently not integrated but adding it would bring the local invocation closer to the real Lambda environment.

Localfunk currently only works with AWS::Serverless::Function and `Sam Deploy` but could work with raw Cloudformation. It could also work with inline lambdas by parsing the template code and dynamically loading the code on each request.

This library only supports calling Python local Python code but the same pattern would work for other languages. Due to the way that the code is loaded and invocated it seems simpler to run Python code from Python but maybe it would work to create a generic CLI tool that could invoke any language.

## Good Idea

Is this a good idea? I am still undecided and I don't currently have a project to test it on thoroughly, try it out and let me know what you think.
