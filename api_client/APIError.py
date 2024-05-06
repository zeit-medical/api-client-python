from pydantic.dataclasses import dataclass


@dataclass
class APIError(BaseException):
    url: str
    status_code: int
    message: str | dict

    def __str__(self):
        if self.status_code:
            return ("API responded with error status code {} for URL {} -- {}").format(
                self.status_code, self.url, self.message
            )

        else:
            return "Can't reach API for URL {} -- {}".format(self.url, self.message)
