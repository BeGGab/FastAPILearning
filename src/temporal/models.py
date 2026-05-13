from dataclasses import dataclass, field
from typing import Optional, List



@dataclass
class BookInput:
    title: str


@dataclass
class CreateAuthorSagaInput:
    request_id: str
    name: str
    books: List[BookInput] = field(default_factory=list)
    biography_text: Optional[str] = None
    year_of_birth: Optional[int] = None
    year_of_death: Optional[int] = None


@dataclass
class CreateBiographyInput:
    request_id: str
    author_id: str
    author_name: str
    biography_text: str
    year_of_birth: int
    year_of_death: int


@dataclass
class DeleteBiographyInput:
    author_id: str
    request_id: str


@dataclass
class DeleteAuthorInput:
    author_id: str
    request_id: str


@dataclass
class CompensationResult:
    attempted: bool
    success: bool
    details: Optional[str] = None


@dataclass
class CreateAuthorSagaResult:
    author_id: Optional[str]
    biography_created: bool
    compensated_author: CompensationResult
    compensated_biography: CompensationResult