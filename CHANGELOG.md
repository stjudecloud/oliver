# Changelog

<!--next-version-placeholder-->

## v1.4.11 (2022-09-05)
### Fix
* Fixes grid style for batches subcommand ([`433cda6`](https://github.com/stjudecloud/oliver/commit/433cda622d66f22557b45e2322f65f460766d12c))

## v1.4.10 (2022-09-03)
### Fix
* In the case of an error, be sure to close the cromwell server ([`662942a`](https://github.com/stjudecloud/oliver/commit/662942acc8fe7e5a07d03cac2cb447e1d3a09715))

## v1.4.9 (2022-09-01)
### Fix
* Fixes case where no jobs have yet started ([`e2bf9ee`](https://github.com/stjudecloud/oliver/commit/e2bf9ee8ee3caa07af766bacdb069e1a4a39d5e8))
* Fixes the very valid objection by pylint ([`346fc78`](https://github.com/stjudecloud/oliver/commit/346fc78afe7bea593101f67ad11ff3bf96560f8c))
* Fixes batching when some workflows aren't started ([`a6303ec`](https://github.com/stjudecloud/oliver/commit/a6303ec5a91ae04014aad34660c2fcb2a6d358aa))
* Fixes wrong command line description for inputs ([`32b852e`](https://github.com/stjudecloud/oliver/commit/32b852e695982c11555de963e5a410b16c99e0a3))

## v1.4.8 (2022-08-29)
### Fix
* Fixes linting error ([`3e4cbaa`](https://github.com/stjudecloud/oliver/commit/3e4cbaad6ec392d26bbf1dfba29e6aa06f419b8a))
* Fixes packaging on pip and updates dependencies ([`e6c7a6a`](https://github.com/stjudecloud/oliver/commit/e6c7a6aaf16b955d1baed7a5df78ea3f49600693))
* Adds boto deps back to main bundle ([`9f3853f`](https://github.com/stjudecloud/oliver/commit/9f3853ffdedff4a90da8c14aeeb505407f1e357b))

## v1.4.7 (2021-11-20)
### Fix
* Removes the wheel package from dependencies altogether ([`083b720`](https://github.com/stjudecloud/oliver/commit/083b7209bd45a2f1cc4ac51b8226498b0bb4af56))

## v1.4.6 (2021-11-20)
### Fix
* Further downgrade wheel to 0.34.0 ([`edb10f1`](https://github.com/stjudecloud/oliver/commit/edb10f1ad5023cffe6322b3f360f33a0fdb6bce5))

## v1.4.5 (2021-11-20)
### Fix
* Fixes build with new version of typed-ast ([`200ad9f`](https://github.com/stjudecloud/oliver/commit/200ad9ff74a03628e6c4ce913a6c2c139348968a))

## v1.4.4 (2021-11-10)
### Fix
* Remove leading '/' from API calls ([#34](https://github.com/stjudecloud/oliver/issues/34)) ([`1bc5521`](https://github.com/stjudecloud/oliver/commit/1bc552147d5c7f0c37b223c76d9a7afe006da0ac))

## v1.4.3 (2021-09-20)
### Fix
* Allow "config" subcommand to skip required args check. Addresses #31 ([#32](https://github.com/stjudecloud/oliver/issues/32)) ([`bc73929`](https://github.com/stjudecloud/oliver/commit/bc739298082b8631cff52096f9658684b8cd11ce))
