
all:
	jekyll build

install-deps:
	gem install jekyll bundler:2.2.16
	xcrun bundle install

serve:
	bundle exec jekyll serve

