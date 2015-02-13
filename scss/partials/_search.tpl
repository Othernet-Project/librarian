.controls {
  padding: 1em 0 0.3em;
  text-align: right;

  .next {
    @include replace-text-with-dimensions('forward.png');
  }

  .prev {
    @include replace-text-with-dimensions('back.png');
  }

  .search {
    display: inline-block;
    padding: 0.2em 1em;
    border: 1px solid darken($light-grey, 10);
    @include border-radius(2px);
    vertical-align: middle;
  }

  span.search {
    height: 34px;
  }
}


