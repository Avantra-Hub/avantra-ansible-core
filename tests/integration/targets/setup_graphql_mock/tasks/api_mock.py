# -*- coding: utf-8 -*-

# Copyright 2022 Avantra

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uvicorn
from fastapi import FastAPI, Response
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from ariadne import load_schema_from_path, QueryType, make_executable_schema
from ariadne.asgi import GraphQL

schema_str = load_schema_from_path("/tmp/mock/schema.graphql")
query = QueryType()


class AuthRequest(BaseModel):
    username: str
    password: str


app = FastAPI()


@app.post("/xn/api/auth/login")
async def login(auth: AuthRequest, response: Response):
    if auth.username != "testuser" or auth.password != "testpwd":
        response.status_code = 401
    else:
        return {"token": "###TestToken###"}


@query.field("systems")
async def resolve_systems():
    return {}


schema = make_executable_schema(schema_str, query)
graphql_app = GraphQLRouter(GraphQL(schema, debug=True))
app.include_router(graphql_app, prefix="/xn/api/graphql")


def main():
    uvicorn.run(app, port=8888)


if __name__ == '__main__':
    main()
