from typing import Any, Optional, Union, Dict
from pydantic import BaseModel


class DataStructure:

    def __init__(
            self,
            status: int = 200,
            success: bool = False,
            message: str = "",
            data: dict = {}
    ) -> None:

        self.status = status
        self.success = success
        self.message = message
        self.data = data

    @property
    def _success(self) -> bool:
        return self.success

    @property
    def _status(self) -> int:
        return self.status

    @_status.setter
    def _status(self, value: int) -> None:
        self.status = value
        if value in range(200, 300):
            self.success = True

    @_success.getter
    def _success(self) -> bool:
        return self.status in range(200, 300) and self.success

    def __repr__(self) -> str:
        params = ', '.join(
            f'{attr}={value!r}'
            for attr, value in self.__dict__.items()
            if not attr.startswith('_')
        )
        return f'{type(self).__name__}({params})'

    def as_dict(self) -> Dict[str, Any]:
        return {
            attr: value for attr, value in self.__dict__.items() if not attr.startswith('_')
        }

    def validate(self, obj: dict):
        data = self.as_dict()
        for i, v in obj.items():
            if i in data:
                setattr(
                    self,
                    i,
                    v
                )

        return self


class DataModel:

    def __init__(
            self,
            data: dict
    ) -> None:
        for key, value in data.items():
            setattr(
                self, key, value
            )

    def as_dict(self) -> Dict[str, Any]:
        return {
            attr: value for attr, value in self.__dict__.items() if not attr.startswith('_')
        }