"""シャード分割ロジックの検証(Discordに接続せず実行可能)。
実行: python -m pytest tests/test_shard_split.py
または: python tests/test_shard_split.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fast_sharded_bot import compute_shard_ids


def test_single_process_covers_all():
    # CLUSTER_COUNT=1(単一プロセス)は全シャード担当
    assert compute_shard_ids(160, 1, 0) == list(range(160))
    assert compute_shard_ids(160, 0, 0) == list(range(160))


def test_clusters_are_disjoint_and_complete():
    # 全クラスタを合わせると重複なく全シャードを網羅する
    for shard_count in (1, 4, 80, 160, 161):
        for cluster_count in (2, 3, 4, 8):
            union = []
            for cid in range(cluster_count):
                union.extend(compute_shard_ids(shard_count, cluster_count, cid))
            assert sorted(union) == list(range(shard_count)), (
                f"shard_count={shard_count} cluster_count={cluster_count} で網羅/重複に問題"
            )
            assert len(union) == len(set(union)), "シャードIDが重複している"


def test_balanced_distribution():
    # 160シャード/4クラスタ → 各40
    for cid in range(4):
        assert len(compute_shard_ids(160, 4, cid)) == 40


if __name__ == "__main__":
    test_single_process_covers_all()
    test_clusters_are_disjoint_and_complete()
    test_balanced_distribution()
    print("OK: 全テスト合格(分割は重複なく全シャードを網羅)")