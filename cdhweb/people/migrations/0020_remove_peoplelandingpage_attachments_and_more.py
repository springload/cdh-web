# Generated by Django 5.0.5 on 2024-06-25 23:57

import django.db.models.deletion
import wagtail.blocks
import wagtail.contrib.routable_page.models
import wagtail.contrib.typed_table_block.blocks
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
from django.db import migrations, models

import cdhweb.pages.blocks.download_block
import cdhweb.pages.blocks.migrated
import cdhweb.pages.blocks.newsletter
import cdhweb.pages.blocks.rich_text


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0019_alter_peoplelandingpage_body_alter_profile_body'),
        ('wagtailcore', '0089_log_entry_data_json_null_to_object'),
        ('wagtailimages', '0025_alter_image_file_alter_rendition_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peoplelandingpage',
            name='attachments',
        ),
        migrations.RemoveField(
            model_name='peoplelandingpage',
            name='body',
        ),
        migrations.RemoveField(
            model_name='peoplelandingpage',
            name='disable_sidebar',
        ),
        migrations.RemoveField(
            model_name='peoplelandingpage',
            name='feed_image',
        ),
        migrations.RemoveField(
            model_name='peoplelandingpage',
            name='short_description',
        ),
        migrations.RemoveField(
            model_name='peoplelandingpage',
            name='short_title',
        ),
        migrations.CreateModel(
            name='PeopleCategoryPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('description', wagtail.fields.RichTextField(blank=True, help_text='Short introduction to the page, aim for max two clear sentences (max. 200 chars). \n        Used to orient the user and help them identify relevancy of the page to meet their needs. ', max_length=200, null=True, verbose_name='Page Summary')),
                ('disable_sidebar', models.BooleanField(default=False, help_text='Hide the sidebar menu showing siblings of this page.')),
                ('body', wagtail.fields.StreamField([('paragraph', cdhweb.pages.blocks.rich_text.RichTextBlock()), ('download_block', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(help_text='Heading for document block', max_length=80, required=False)), ('description', wagtail.blocks.TextBlock(help_text='A description to display with the download file (150 characters maximum).', max_length=150, required=False)), ('documents', wagtail.blocks.ListBlock(cdhweb.pages.blocks.download_block.FileBlock, help_text='Upload at least 1 and maximum 10 files. Each file size should be less than 5MB.', max_num=10, min_num=1))])), ('cta_block', wagtail.blocks.StructBlock([('introduction', wagtail.blocks.TextBlock(help_text='Short introduction to the action you want users to take. Ideal: 80 characters or less (Max: 100 characters).', max_length=100, required=False)), ('cta_buttons', wagtail.blocks.StreamBlock([('internal_link', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock()), ('link_text', wagtail.blocks.CharBlock(label='Button text', max_length=40, required=True))])), ('external_link', wagtail.blocks.StructBlock([('link_url', wagtail.blocks.URLBlock(label='URL')), ('link_text', wagtail.blocks.CharBlock(label='Button text', max_length=40, required=True))]))], max_num=2, min_num=1))])), ('accordion_block', wagtail.blocks.StructBlock([('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))], required=False)), ('description', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False)), ('accordion_items', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True, verbose_name='Accordion Title')), ('body', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul', 'document-link', 'h3', 'h4'], help_text='Only use H3 if you have not set an overall heading for the accordion block.'))])))])), ('video_block', wagtail.blocks.StructBlock([('video', wagtail.blocks.URLBlock(help_text='A YouTube URL. Link to a specifc video or playlist.')), ('accessibility_description', wagtail.blocks.CharBlock(help_text='Use this to describe the video. It is used as an accessibility attribute mainly for screen readers.', required=False)), ('transcript', wagtail.blocks.RichTextBlock(features=['bold', 'link', 'document-link'], required=False)), ('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))], required=False))])), ('embed', wagtail.blocks.StructBlock([('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))], required=False)), ('video_url', wagtail.embeds.blocks.EmbedBlock(help_text='This should be used for videos from Princeton\'s Media Central. Copy the "oEmbed URL" from the "Share" menu')), ('accessibility_description', wagtail.blocks.CharBlock(help_text='Use this to describe the video. It is used as an accessibility attribute mainly for screen readers.', required=True)), ('transcript', wagtail.blocks.RichTextBlock(features=['bold', 'link', 'document-link'], required=False))])), ('pull_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic'], help_text='Pull a small section of content out as an "aside" to give it emphasis.', max_length=100, required=True)), ('attribution', wagtail.blocks.RichTextBlock(features=['bold', 'link'], help_text='Optional attribution', max_length=60, required=False))])), ('note', wagtail.blocks.StructBlock([('heading', wagtail.blocks.TextBlock(help_text='Optional heading', required=False)), ('message', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ul', 'ol'], help_text='Note message up to 750 chars', max_length=750, required=True))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Image', required=True)), ('caption', wagtail.blocks.RichTextBlock(features=['italic', 'bold', 'link'], help_text='A short caption for the image.', max_length=180, required=False)), ('credit', wagtail.blocks.RichTextBlock(features=['italic', 'bold', 'link'], help_text='A credit line or attribution for the image.', max_length=80, required=False)), ('alt_text', wagtail.blocks.CharBlock(help_text='Describe the image for screen readers', max_length=80, required=False)), ('size', wagtail.blocks.ChoiceBlock(choices=[('small', 'small'), ('medium', 'medium'), ('large', 'large')], label='Image Size'))])), ('feature', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True)), ('feature_text', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'ol', 'ul'], max_length=400)), ('image', wagtail.images.blocks.ImageChooserBlock(label='Image', required=True)), ('alt_text', wagtail.blocks.CharBlock(help_text='Describe the image for screen readers.', max_length=80, required=False)), ('cta_buttons', wagtail.blocks.StreamBlock([('internal_link', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock()), ('link_text', wagtail.blocks.CharBlock(label='Button text', max_length=40, required=True))])), ('external_link', wagtail.blocks.StructBlock([('link_url', wagtail.blocks.URLBlock(label='URL')), ('link_text', wagtail.blocks.CharBlock(label='Button text', max_length=40, required=True))]))], max_num=2, min_num=0, required=False))])), ('table', wagtail.blocks.StructBlock([('caption', wagtail.blocks.CharBlock(help_text='Table caption', label='Caption', required=False)), ('notes', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], help_text='Primarily for using for footnotes from cells with asterisks', label='Table notes', required=False)), ('table', wagtail.contrib.typed_table_block.blocks.TypedTableBlock([('rich_text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul', 'h3']))], help_text='It is recommended to use a minimal number of columns, to ensure the table is usable on mobile and desktop.', max_num=1, min_num=1))])), ('newsletter', cdhweb.pages.blocks.newsletter.NewsletterBlock()), ('heading', wagtail.blocks.StructBlock([('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))]))])), ('tile_block', wagtail.blocks.StructBlock([('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))], help_text='Heading for this tile block', required=False)), ('description', wagtail.blocks.CharBlock(help_text='Description for this tile block', label='Description', required=False)), ('see_more_link', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(help_text='Choose a page to link to', label='Wagtail Page', required=False)), ('title', wagtail.blocks.CharBlock(help_text='Set title for this link', label='Link title', max_length=80, required=False))], help_text="'See more' link", required=False)), ('featured', wagtail.blocks.BooleanBlock(default=False, help_text='Check this checkbox to create a visually distinct tile block that stands out from regular tiles on the page.', required=False)), ('tiles', wagtail.blocks.StreamBlock([('internal_page_tile', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(required=True))])), ('external_page_tile', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Title for this tile.', label='Tile Title', max_length=100, required=True)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='Image for this tile.', label='Tile Image', required=False)), ('summary', wagtail.blocks.CharBlock(help_text='Summary for this tile.', label='Tile Summary', max_length=200, required=False)), ('external_link', wagtail.blocks.URLBlock(required=True))]))], min_num=1, required=True))])), ('article_tile_block', wagtail.blocks.StructBlock([('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))], help_text='Heading for this tile block', required=False)), ('description', wagtail.blocks.CharBlock(help_text='Description for this tile block', label='Description', required=False)), ('landing_page', wagtail.blocks.PageChooserBlock(help_text='Select the Blog Landing Page whose child pages you want to show as tiles in this block.', page_type=['blog.BlogLandingPage'], required=True)), ('max_articles', wagtail.blocks.ChoiceBlock(choices=[(2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')], help_text='Define the maximum number of tiles to show in this group.', icon='placeholder')), ('see_more_link', wagtail.blocks.CharBlock(default='See All', help_text='Set text for the link which takes you to the landing page', label='Link title', max_length=80, required=False))])), ('event_tile_block', wagtail.blocks.StructBlock([('show_in_jumplinks', wagtail.blocks.BooleanBlock(default=False, help_text="Link to this block in the jumplinks list (when 'Show jumplinks' is enabled in Page settings)", required=False)), ('heading', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(max_length=80, required=True))], help_text='Heading for this tile block', required=False)), ('description', wagtail.blocks.CharBlock(help_text='Description for this tile block', label='Description', required=False)), ('landing_page', wagtail.blocks.PageChooserBlock(help_text='Select the Event Landing Page whose child pages you want to show as tiles in this block.', page_type=['events.EventsLandingPage'], required=True)), ('max_articles', wagtail.blocks.ChoiceBlock(choices=[(2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')], help_text='Define the maximum number of tiles to show in this group.', icon='placeholder')), ('see_more_link', wagtail.blocks.CharBlock(default='See All', help_text='Set text for the link which takes you to the landing page', label='Link title', max_length=80, required=False))])), ('migrated', cdhweb.pages.blocks.migrated.MigratedBlock())], blank=True, help_text='Put content for the body of the page here. Start with using the + button.', use_json_field=True, verbose_name='Page content')),
                ('attachments', wagtail.fields.StreamField([('document', wagtail.documents.blocks.DocumentChooserBlock()), ('link', wagtail.snippets.blocks.SnippetChooserBlock('cdhpages.ExternalAttachment'))], blank=True, use_json_field=True)),
                ('short_title', models.CharField(blank=True, default='', help_text='Displayed on tiles, breadcrumbs etc., not on page itself. ', max_length=80, verbose_name='Short title')),
                ('short_description', models.TextField(blank=True, help_text='A short description of the content for promotional or navigation purposes. Displayed on tiles, not on page itself.', max_length=130, verbose_name='Short description')),
                ('category', models.CharField(choices=[('staff', 'Staff'), ('students', 'Students'), ('affiliates', 'Affiliates'), ('executive_committee', 'Executive Committee')])),
                ('feed_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('hero_image', models.ForeignKey(blank=True, help_text='Optional image to support intent of the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model, wagtail.contrib.routable_page.models.RoutablePageMixin),
        ),
    ]
