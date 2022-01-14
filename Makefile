
all:
	jekyll build

install-deps:
	xcrun bundle install

serve:
	bundle exec jekyll serve

