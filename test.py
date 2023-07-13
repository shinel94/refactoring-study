from unittest import TestCase, main
from refactor import main as get_result

class Study(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_main_result(self):
        result = get_result().split('\n')

        with open('./data/result.txt', 'r', encoding='utf-8') as f:
            solution = f.readlines()
        for r,s in zip(result, solution):
            self.assertEqual(r, s.rstrip())



if __name__ == "__main__":
    main()