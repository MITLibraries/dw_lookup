;
// return $ back to any previous jQuery declared on page
var jquery_1_11_2 = $.noConflict(true);

(function($) {
    var authorLookupObj = new authorLookup();

    function authorLookup(params) {
        var options = _.extend({
            authorLookupUrl: '/author/',

            /* number of chars required in the search field to make a request to the
             * server.
             */
            charLowerLimit: 3,

            /* ms until lookup is started
             * allows user to type a complete word before it is sent to the server
             * vs sending on each keystroke
             */
            typeAheadTimeout: 500,

            $elementToAttachTo: $('#aspect_administrative_item_EditItemMetadataForm_field_value'),

            $fieldToOverride: $('#aspect_administrative_item_EditItemMetadataForm_field_field')
        }, params);
    
        /* override metadata name field
         * when selecting mitauthor, create and add lookup block
         * else, delete the lookup block, if it exists
         */
        options.$fieldToOverride.change($.proxy(function(event) {
            if (event.target.value == 75) {
                buildAuthorLookupBlock.call(this);
            }
            else {
                if (this.$authorLookupBlock) {
                    this.$authorLookupBlock.remove();
                }
            }
        }, this));

        /* put these in separate files because multi-line text in js looks messy */
        $.get('/static/js/templates/static-block.html', $.proxy(function (raw_template) {
            this.staticBlockTemplate = _.template(raw_template);
        }, this), 'html');
        $.get('/static/js/templates/table-row.html', $.proxy(function (raw_template) {
            this.tableRowTemplate = _.template(raw_template, {variable: 'record'});
        }, this), 'html');

        function buildAuthorLookupBlock() {
            /* update an existing input field to allow type-ahead lookup feature.
             * typing a partial name will call remote server and return list of
             * possible matches. Clicking the [+] "icon" will make that id the value
             * of the element this is "attached" to.
             */
            this.$authorLookupBlock = $(this.staticBlockTemplate());
            this.$authorLookupSearch = this.$authorLookupBlock.find("#author-lookup-search");
            this.$authorLookupStatus = this.$authorLookupBlock.find("#author-lookup-status");
            this.$authorLookupTableBody = this.$authorLookupBlock.find("#author-lookup-tbody");


            /* when search field has > 2 chars, send string to lookup API
             * update results with response
             */
            this.$authorLookupSearch.on("input", $.proxy(handler, this));

            options.$elementToAttachTo.before(this.$authorLookupBlock);
        }

        function handler(event) {
            var value = $(event.target).val();

            if ($(event.target).data("lastval") != value) {
                /* lastval allows us to ignore keystrokes unless they
                 * actually change the lookup value
                 */
                $(event.target).data("lastval", value);

                /* clear previous results/status */
                this.$authorLookupTableBody.html('');
                this.$authorLookupStatus.html('');

                /* timer counts down to request to server
                 * if user changes the value before request, clear the "queued"
                 * request and build another based on the new value
                 * then reset the timer
                 */
                clearTimeout(this.timer);

                /* woops, if a previous request was already sent but not
                 * complete, we have to ignore the results of that request
                 */
                if (this.$request && this.$request.readyState !== 4) {
                    this.$request.abort();
                }

                if (value.length >= options.charLowerLimit) {
                    this.timer = setTimeout(
                        function() {
                            getAuthorData.call(this, value);
                        }.bind(this),
                        options.typeAheadTimeout
                    );
                }
            }
        }

        function getAuthorData(value) {
            this.$authorLookupSearch.addClass('al-loading'); // spinner

            this.$request = $.ajax({
                url: options.authorLookupUrl +'?name_partial='+ value,
                dataType: 'json',
                context: this
            })
                .done(function(data) {
                    var rows = [];
                    
                    $.each(data.results, function(index, record) {
                        rows.push(this.tableRowTemplate(record));
                    }.bind(this));

                    this.$authorLookupTableBody.append(rows.join(''));
                })
                .fail(function(jqXHR, statusText, errorThrown) {
                    /* differentiate between a user abort action
                     * eg a change of the string in the search
                     * box, and an actual error.
                     */
                    if (statusText == 'abort') {
                        console.log('user aborted');
                    }
                    else {
                        this.$authorLookupStatus.html('ERR: '+ statusText);
                    }

                    console.log(jqXHR, statusText, errorThrown);
                })
                .always(function() {
                    /* click handler for add button next to each
                     * result. Possible to do this while building
                     * the list?
                     */
                    this.$authorLookupTableBody.find('tr').click(function() {
                        $('#aspect_administrative_item_EditItemMetadataForm_field_value').html($(this).attr('data-name'));
                    });

                    this.$authorLookupSearch.removeClass('al-loading');
                });
        }
    }
}(jquery_1_11_2));