from enum import Enum
import pandas as pd

from models.enums import AccountType, PlatformType
from utils.case_converter import title_to_snake


def get_mapping_and_grouping_list(brokers_df):
    tree_enum_mapping = {
        "Type": AccountType,
        "Broker": Enum(
            "BrokerType",
            {title_to_snake(item): item for item in brokers_df["name"].tolist()},
            type=str,
        ),
        "Platform": PlatformType,
    }
    grouping_list = list(tree_enum_mapping.keys())

    return tree_enum_mapping, grouping_list


def resolve_enum_value(enum_class, key_val: str):
    try:
        member_name = key_val.split(".")[-1]
        return getattr(enum_class, member_name).value
    except (AttributeError, TypeError):
        return key_val


def build_tree(df: pd.DataFrame, group_keys: list, path_parts: list = [], enum_mapping: dict = {}, ungroup_keys: list = [], is_root=True):
    if df.empty:
        return []

    if group_keys == []:
        leaves = []
        for _, row in df.iterrows():
            label_parts = [row["name"], row["login"]]
            for key in ungroup_keys:
                if key.lower() in row and pd.notna(row[key.lower()]):
                    enum_cls = enum_mapping.get(key)
                    value = resolve_enum_value(enum_cls, str(row[key.lower()]))
                    label_parts.append(value)
            label = " ".join(label_parts)

            leaf = {"label": label, "id": row["id"]}
            leaves.append(leaf)

        if is_root:
            return [{"label": "All Accounts", "id": "All-Accounts", "children": leaves}]
        else:
            return leaves

    current_key = group_keys[0].lower()
    tree = []

    for key_val, group_df in df.groupby(current_key, dropna=False):
        enum_cls = enum_mapping.get(current_key)
        value = resolve_enum_value(enum_cls, str(key_val))
        new_path = path_parts + [value]

        node = {
            "label": value,
            "id": "-".join(new_path),
        }
        children = build_tree(group_df, group_keys[1:], new_path, enum_mapping=enum_mapping, ungroup_keys=ungroup_keys, is_root=False)
        if children:
            node["children"] = children
        tree.append(node)
    return tree
