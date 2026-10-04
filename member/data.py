import pickle
from pathlib import Path

from member.core import Member
from member.lcr import get_directory_lcr
from member.standard import get_directory_standard


def save_member_data(data: list[Member], filepath: Path):
    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True)

    serialized = pickle.dumps(data)
    with open(file=filepath, mode="wb") as file:
        file.write(serialized)


def load_member_data(filepath: Path) -> list[Member]:
    with open(file=filepath, mode="rb") as file:
        return pickle.loads(file.read())


def combine_part_data(data_path: Path) -> list[Member]:
    data: list[Member] = []
    index = 0
    part_path = data_path.with_name(f"{data_path.stem}_{index}{data_path.suffix}")
    while part_path.is_file():
        data.extend(load_member_data(part_path))
        index += 1
        part_path = data_path.with_name(f"{data_path.stem}_{index}{data_path.suffix}")

    return data


def get_member_data(
    username: str, password: str, max_query: int = 50, use_lcr: bool = False
) -> list[Member]:
    data_path = Path("data/member_data.pkl")
    if data_path.is_file():
        data = load_member_data(data_path)
        return data
    finding_path = True
    index = 0
    part_path = Path()
    while finding_path:
        if data_path.with_name(f"{data_path.stem}_{index}{data_path.suffix}").is_file():
            index += 1
        else:
            part_path = data_path.with_name(
                f"{data_path.stem}_{index}{data_path.suffix}"
            )
            finding_path = False

    if use_lcr:
        part_data = get_directory_lcr(
            username,
            password,
            start_index=max_query * index,
            end_index=(max_query * (index + 1)),
        )
    else:
        part_data = get_directory_standard(
            username,
            password,
            start_index=max_query * index,
            end_index=(max_query * (index + 1)),
        )
    if len(part_data) != 0:
        save_member_data(part_data, Path(part_path))

    data = combine_part_data(data_path)
    return data
