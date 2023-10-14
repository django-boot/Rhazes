## How to contribute to Rhazes

#### **Did you find a bug?**

* **Do not open up a GitHub issue if the bug is a django framework vulnerability**

* **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/django-boot/Rhazes/issues).

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/django-boot/Rhazes/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

#### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.

* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

* Before submitting your code, **make sure you ran all of our `pre-commit` pipeline in your branch/fork**. To do so, follow the steps below:

  ```shell
  pre-commit install
  pre-commit install --hook-type commit-msg

  # now commit
  git commit -m "message here should follow conventional commit messages"

  # If you have already committed your changes but still want to run pre-commit pipeline:
  pre-commit run --all-files
  ```

Thanks! :heart:

Django Boot - Rhazes
