"""Bagging cây: bootstrap, hard voting và đánh giá out-of-bag tự triển khai."""

from numbers import Integral

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import check_is_fitted, validate_data


class ManualBagging(ClassifierMixin, BaseEstimator):
    """Học các cây trên mẫu bootstrap rồi tổng hợp bằng đa số nhãn.

    Mỗi cây lấy đúng N lượt có hoàn lại từ N mẫu train. Cây cơ sở dùng
    scikit-learn; việc lấy mẫu, bỏ phiếu và OOB được viết tường minh.
    Cột phiếu theo thứ tự ``classes_``; hòa phiếu chọn lớp đầu tiên.
    Tỷ lệ phiếu KHÔNG phải xác suất đã hiệu chỉnh.

    ``oob_score_`` chỉ tính trên mẫu có ít nhất một cây OOB, dùng hard
    voting. Mẫu không có cây OOB có hàng NaN trong oob_decision_function_.
    """

    def __init__(self, n_estimators=51, max_depth=4, random_state=42, oob_score=True):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.oob_score = oob_score

    def _check_parameters(self):
        if isinstance(self.n_estimators, bool) or not isinstance(self.n_estimators, Integral) or self.n_estimators < 1:
            raise ValueError("n_estimators phải là số nguyên >= 1")
        if self.max_depth is not None and (
            isinstance(self.max_depth, bool) or not isinstance(self.max_depth, Integral) or self.max_depth < 1
        ):
            raise ValueError("max_depth phải là số nguyên >= 1 hoặc None")
        if self.random_state is not None and (
            isinstance(self.random_state, bool) or not isinstance(self.random_state, Integral)
            or not 0 <= self.random_state < 2**32
        ):
            raise ValueError("random_state phải là số nguyên từ 0 đến 2**32-1 hoặc None")
        if not isinstance(self.oob_score, (bool, np.bool_)):
            raise ValueError("oob_score phải là True hoặc False")

    def fit(self, X, y):
        self._check_parameters()
        X, y = validate_data(self, X, y, reset=True, dtype=float)
        check_classification_targets(y)
        self.classes_, encoded = np.unique(y, return_inverse=True)
        rng = np.random.default_rng(self.random_state)
        self.estimators_ = []
        self.estimators_samples_ = []
        self.bootstrap_preview_ = []
        n_samples = len(X)
        oob_votes = np.zeros((n_samples, len(self.classes_)), dtype=np.int64)

        # Xóa trạng thái OOB cũ nếu refit với oob_score=False.
        for name in ("oob_counts_", "oob_vote_counts_", "oob_decision_function_", "oob_score_", "oob_coverage_"):
            if hasattr(self, name):
                delattr(self, name)

        for _ in range(self.n_estimators):
            indices = rng.integers(0, n_samples, size=n_samples)
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
            tree.fit(X[indices], encoded[indices])
            self.estimators_.append(tree)
            self.estimators_samples_.append(indices)
            self.bootstrap_preview_.append(indices[:10].tolist())
            if self.oob_score:
                # Chỉ các mẫu KHÔNG có trong bootstrap mới được nhận phiếu OOB.
                unseen = np.flatnonzero(np.bincount(indices, minlength=n_samples) == 0)
                if len(unseen):
                    predicted = tree.predict(X[unseen]).astype(int)
                    np.add.at(oob_votes, (unseen, predicted), 1)

        self.trees_ = self.estimators_  # Giữ tương thích với bản demo ban đầu.
        if self.oob_score:
            self.oob_vote_counts_ = oob_votes
            self.oob_counts_ = oob_votes.sum(axis=1)
            covered = self.oob_counts_ > 0
            self.oob_coverage_ = float(covered.mean())
            self.oob_decision_function_ = np.full(oob_votes.shape, np.nan)
            self.oob_decision_function_[covered] = oob_votes[covered] / self.oob_counts_[covered, None]
            self.oob_score_ = (
                float(accuracy_score(encoded[covered], oob_votes[covered].argmax(axis=1)))
                if covered.any() else float("nan")
            )
        return self

    def votes(self, X):
        """Trả số phiếu nguyên, kích thước (số quan sát, số lớp)."""
        check_is_fitted(self, ["estimators_", "classes_"])
        X = validate_data(self, X, reset=False, dtype=float)
        counts = np.zeros((len(X), len(self.classes_)), dtype=np.int64)
        rows = np.arange(len(X))
        for tree in self.estimators_:
            # Cây học nhãn encoded; kể cả bootstrap thiếu một lớp vẫn ánh xạ đúng.
            predicted = tree.predict(X).astype(int)
            np.add.at(counts, (rows, predicted), 1)
        return counts

    def predict_vote_fraction(self, X):
        """Tỷ lệ hard-vote của các cây, không phải predict_proba."""
        return self.votes(X) / len(self.estimators_)

    def predict(self, X):
        counts = self.votes(X)
        return self.classes_[counts.argmax(axis=1)]
