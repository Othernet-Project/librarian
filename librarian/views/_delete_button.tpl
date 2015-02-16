<form class="delete-button" action="{{ i18n_path('/delete/%s' % meta.md5) }}" method="POST">
    <button>
        <span class="icon">
            <span class="altlabel"></span> 
            <span class="fulllabel">Delete</span>
        </span>
    </button>
</form>
