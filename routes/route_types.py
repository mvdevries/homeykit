from typing import Any, Never

type RouteQuery = dict[str, str]
type RouteParams = dict[str, str]
type EmptyBody = dict[Never, Never]
type JsonBody = dict[str, Any]
