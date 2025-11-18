from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PaperAuthor(BaseModel):
    id: str
    name: str
    affiliation: str


class Paper(BaseModel):
    id: str
    title: str
    year: int
    source: str
    cited_by: int
    doi: str
    link: str
    authors: List[str]
    document_type: Optional[str] = None
    eid: Optional[str] = None


class Author(BaseModel):
    id: str
    name: str
    affiliation: str
    paper_count: int
    paper_ids: List[str] = []


class University(BaseModel):
    id: str
    name: str
    paper_count: int
    author_count: int
    authors: List[Author] = []


class Country(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    paper_count: int
    universities: List[University] = []


class AggregatedData(BaseModel):
    countries: List[Country]
    last_updated: datetime


class Stats(BaseModel):
    total_papers: int
    total_countries: int
    total_universities: int
    total_authors: int
