"""
AEdificium Server API
"""

import sqlalchemy
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from .db import create_db_and_tables, get_session
from .models import (
    RegisteredTeam,
    RegistrationRequest,
    RegistrationResponse,
    generate_id,
)
from .problem_session import MapField, ProblemSession

app = FastAPI()

# in-memory user problem sessions
SESSIONS = {}


@app.on_event("startup")
async def startup():
    """
    Create the db on starup
    """
    create_db_and_tables()


@app.post("/register", response_model=RegistrationResponse)
async def register(
    registration: RegistrationRequest, session: Session = Depends(get_session)
):
    """
    Register a team and get an id that can be used for subsequent requests
    """
    team = RegisteredTeam(
        id=generate_id(registration.email),
        name=registration.name,
        pl=registration.pl,
        email=registration.email,
    )
    session.add(team)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as err:
        err_string = str(err)
        if "registeredteam.name" in err_string:
            raise HTTPException(
                status_code=409, detail="A team with that name already exists"
            ) from err
        if "registeredteam.email" in err_string:
            raise HTTPException(
                status_code=409, detail="A team with that email already exists"
            ) from err
    session.refresh(team)

    return team


class SelectRequest(BaseModel):
    """
    Request to select a problem
    """

    id: str
    problemName: str


class SelectResponse(BaseModel):
    """
    Returns the name of the selected problem
    """

    problemName: str


@app.post("/select")
async def select(  # pylint: disable=redefined-outer-name
    select: SelectRequest, session: Session = Depends(get_session)
) -> SelectResponse:
    """
    Select a problem to start a new problem session.
    NOTE: selecting a problem will trash the current problem session and start a new one
    """
    team = session.get(RegisteredTeam, select.id)
    if not team:
        raise HTTPException(status_code=404, detail="No team found with that ID")

    SESSIONS[team.id] = ProblemSession(select.problemName)

    return SelectResponse(problemName=select.problemName)


class ExploreRequest(BaseModel):
    """
    Request to explore a problem
    """

    id: str
    plans: list[str]


class ExploreResponse(BaseModel):
    """
    Result of rexploring a problem
    """

    results: list[list[int]]
    queryCount: int


@app.post("/explore")
async def explore(exploration: ExploreRequest) -> ExploreResponse:
    """
    Explore the current problem session and get back results
    This will increase the query_count of the problem session by one for each plan,
    plus one for the request
    """
    if not exploration.id in SESSIONS:
        raise HTTPException(status_code=404, detail="No problem has been selected")
    problem_session = SESSIONS[exploration.id]

    return ExploreResponse(
        results=problem_session.explore_all(exploration.plans),
        queryCount=problem_session.query_count,
    )


class GuessRequest(BaseModel):
    """
    Request to guess the map of the aedificium
    """

    id: str
    map: MapField


class GuessResponse(BaseModel):
    """
    Result of the guess
    """

    correct: bool


@app.post("/guess")
async def guess(guess_request: GuessRequest) -> GuessResponse:
    """
    Guess the map of the aedificium - from the task:

        The field correct is true iff the submitted
        map is equivalent to the map generated when
        /select was invoked. By equivalent, we mean
        that they have the same number of rooms, and
        that they are indistinguishable by any route
        plan — if there is no route plan that demonstrates the difference between two maps of the
        same size, they are considered equivalent
    """
    if not guess_request.id in SESSIONS:
        raise HTTPException(status_code=404, detail="No problem has been selected")
    problem_session = SESSIONS[guess_request.id]

    return GuessResponse(
        correct=problem_session.guess(guess_request.map),
    )
