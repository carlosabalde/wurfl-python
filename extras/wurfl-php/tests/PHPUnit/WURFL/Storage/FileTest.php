<?php
/**
 * test case
 */
require_once dirname(__FILE__).'/../classautoloader.php';

/**
 * test case.
 */
class WURFL_Storage_FileTest extends PHPUnit_Framework_TestCase {

    const STORAGE_DIR = "../../../resources/storage";

    public function setUp() {
        WURFL_FileUtils::mkdir($this->storageDir());
    }

    public function tearDown() {
        WURFL_FileUtils::rmdir($this->storageDir());
    }

    public function testShouldTryToCreateTheStorage() {
        $cachepath = $this->realpath(self::STORAGE_DIR . "/cache");
        $params = array(
            "dir" => $cachepath
        );
        new WURFL_Storage_File($params);
        $this->assertStorageDirectoryIsCreated($cachepath);
        WURFL_FileUtils::rmdir($cachepath);
    }

    private function realpath($path) {
        return dirname(__FILE__) . DIRECTORY_SEPARATOR . $path;
    }

    private function assertStorageDirectoryIsCreated($dir) {
        $this->assertTrue(file_exists($dir) && is_writable($dir));
    }

    public function testNeverToExpireItems() {
        $params = array(
            "dir" => $this->storageDir(),
            WURFL_Configuration_Config::EXPIRATION => 0);

        $storage = new WURFL_Storage_File($params);

        $storage->save("foo", "foo");
        sleep(1);
        $this->assertEquals("foo", $storage->load("foo"));

    }

    public function testShouldRemoveTheExpiredItem() {

        $params = array(
            "dir" => $this->storageDir(),
            WURFL_Configuration_Config::EXPIRATION => 1);

        $storage = new WURFL_Storage_File($params);

        $storage->save("item2", "item2");
        $this->assertEquals("item2", $storage->load("item2"));
        sleep(2);
        $this->assertEquals(NULL, $storage->load("item2"));
    }

    private function storageDir() {
        return dirname(__FILE__) . DIRECTORY_SEPARATOR . self::STORAGE_DIR;
    }

}
